"""Use a real endless multipart MJPEG server, not an image-attribute assertion."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http.client
from pathlib import Path
import sys
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from klipperscreencam.stream import StreamProxy, multipart_parts

JPEG = (Path(__file__).parent / "fixtures/frame.jpg").read_bytes()


class Source:
    def __init__(self, interval=0.02):
        self.lock = threading.Lock()
        self.accepted = 0
        self.active = 0
        self.sent = 0
        self.closed = threading.Event()
        self.shutdown = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                if self.path == "/redirect":
                    self.send_response(302)
                    self.send_header("Location", "/stream")
                    self.end_headers()
                    return
                if self.path == "/not-mjpeg":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"not a video")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.end_headers()
                with owner.lock:
                    owner.accepted += 1
                    owner.active += 1
                frame = (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                         + str(len(JPEG)).encode() + b"\r\n\r\n" + JPEG + b"\r\n")
                try:
                    while not owner.shutdown.is_set():
                        self.wfile.write(frame)
                        self.wfile.flush()
                        with owner.lock:
                            owner.sent += len(frame)
                        owner.shutdown.wait(interval)
                except OSError:
                    pass
                finally:
                    with owner.lock:
                        owner.active -= 1
                    owner.closed.set()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def close(self):
        self.shutdown.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.source = Source()
        self.proxy = StreamProxy(timeout=2)
        self.responses = []

    def tearDown(self):
        self.proxy.close()
        for response in self.responses:
            response.close()
        self.source.close()

    def open_stream(self, url):
        response = urlopen(url, timeout=2)
        self.responses.append(response)
        self.assertIn("multipart/x-mixed-replace", response.headers["Content-Type"])
        chunk = response.read1(65536)
        self.assertIn(b"--frame", chunk)
        return response

    def test_stop_closes_actual_upstream_and_bytes_stop(self):
        url = self.proxy.prepare(self.source.url + "/stream")
        self.open_stream(url)
        self.assertEqual(self.source.active, 1)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2), "Camera TCP connection remained open")
        self.assertEqual(self.source.active, 0)
        sent_after_close = self.source.sent
        time.sleep(0.1)
        self.assertEqual(self.source.sent, sent_after_close, "Frames still flowing while off")

    def test_display_sleep_closes_real_camera_connection(self):
        from klipperscreencam.power import DisplayPower
        url = self.proxy.prepare(self.source.url + "/stream")
        self.open_stream(url)
        events = []
        power = DisplayPower(self.proxy.stop, events.append)
        power.update(False)
        self.assertTrue(self.source.closed.wait(2))
        sent = self.source.sent
        time.sleep(0.1)
        self.assertEqual(self.source.sent, sent)
        self.assertEqual(events, [True])
        self.assertIsNone(self.proxy.current)
        power.update(True)
        self.assertIsNone(self.proxy.current)  # Wake lets the UI decide manual pause.
        self.assertEqual(events, [True, False])

    def test_stale_browser_retry_cannot_restart_stopped_stream(self):
        url = self.proxy.prepare(self.source.url + "/stream")
        self.open_stream(url)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2))
        accepted = self.source.accepted
        with self.assertRaises(HTTPError) as error:
            urlopen(url, timeout=2)
        self.assertEqual(error.exception.code, 410)
        self.assertEqual(self.source.accepted, accepted)
        self.assertEqual(self.source.active, 0)

    def test_preparing_without_browser_request_does_not_open_camera(self):
        self.proxy.prepare(self.source.url + "/stream")
        self.assertEqual(self.source.accepted, 0)
        self.proxy.stop()
        self.assertEqual(self.source.accepted, 0)

    def test_only_one_request_can_claim_a_stream(self):
        url = self.proxy.prepare(self.source.url + "/stream")
        self.open_stream(url)
        with self.assertRaises(HTTPError) as error:
            urlopen(url, timeout=2)
        self.assertEqual(error.exception.code, 410)
        self.assertEqual(self.source.accepted, 1)

    def test_reselection_closes_previous_connection_and_uses_fresh_token(self):
        old = self.proxy.prepare(self.source.url + "/stream")
        self.open_stream(old)
        new = self.proxy.prepare(self.source.url + "/stream")
        self.assertNotEqual(new, old)
        self.assertTrue(self.source.closed.wait(2))
        self.source.closed.clear()
        self.open_stream(new)
        self.assertEqual(self.source.accepted, 2)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2))

    def test_redirect_is_followed_and_still_cancellable(self):
        url = self.proxy.prepare(self.source.url + "/redirect")
        self.open_stream(url)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2))

    def test_local_fps_cap_drops_frames_without_changing_other_client(self):
        self.proxy.close()
        self.proxy = StreamProxy(timeout=2, max_fps=5)
        direct = urlopen(self.source.url + "/stream", timeout=2)
        self.responses.append(direct)
        response = urlopen(self.proxy.prepare(self.source.url + "/stream"), timeout=2)
        self.responses.append(response)
        session = self.proxy.current
        times = []
        for _ in range(5):
            self.assertEqual(response.readline(), b"--frame\r\n")
            headers = {}
            while True:
                line = response.readline()
                if line == b"\r\n":
                    break
                key, value = line.decode().split(":", 1)
                headers[key.lower()] = value.strip()
            self.assertEqual(response.read(int(headers["content-length"])), JPEG)
            self.assertEqual(response.read(2), b"\r\n")
            times.append(time.monotonic())
        self.assertGreaterEqual(times[-1] - times[0], 0.7)
        self.assertLess(times[-1] - times[0], 1.8)
        self.assertGreater(self.source.sent, session.bytes_forwarded * 2)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2))
        # The independent remote-style consumer keeps receiving original frames.
        before = self.source.sent
        time.sleep(0.1)
        self.assertGreater(self.source.sent, before)
        self.assertGreaterEqual(self.source.active, 1)

    def test_live_fps_switch_to_unlimited_keeps_same_connection(self):
        self.proxy.set_max_fps(1)
        response = urlopen(self.proxy.prepare(self.source.url + "/stream"), timeout=2)
        self.responses.append(response)
        self.assertIn(b"--frame", response.read1(65536))
        session = self.proxy.current
        self.proxy.set_max_fps(None)
        started = time.monotonic()
        frames = multipart_parts(response, b"--frame", threading.Event())
        for _ in range(4):
            self.assertIn(JPEG, next(frames))
        self.assertLess(time.monotonic() - started, 0.8)
        self.assertEqual(self.source.accepted, 1)
        self.assertIs(self.proxy.current, session)
        self.proxy.set_max_fps(20)
        self.assertEqual(self.proxy.max_fps, 20)
        self.proxy.stop()
        self.assertTrue(self.source.closed.wait(2))

    def test_fps_change_while_off_does_not_open_camera(self):
        for value in (10, 20, 30, None):
            self.proxy.set_max_fps(value)
            self.assertEqual(self.proxy.max_fps, value)
        self.assertEqual(self.source.accepted, 0)
        self.assertIsNone(self.proxy.current)
        for value in (0, -1, 121, True, 15.5, "unlimited"):
            with self.assertRaises(ValueError):
                self.proxy.set_max_fps(value)

    def test_all_live_presets_change_actual_forwarded_frame_rate(self):
        self.source.close()
        self.source = Source(interval=0.005)
        response = urlopen(self.proxy.prepare(self.source.url + "/stream"), timeout=2)
        self.responses.append(response)
        self.assertIn(b"--frame", response.read1(65536))
        rates = []
        for limit in (10, 20, 30, None):
            self.proxy.set_max_fps(limit)
            time.sleep(0.08)
            self.proxy.sample_stats()
            time.sleep(0.65)
            stats = self.proxy.sample_stats()
            with self.subTest(limit=limit, stats=stats):
                self.assertEqual(stats["maxFps"], limit)
                self.assertGreater(stats["sourceFps"], 35)
                if limit is None:
                    self.assertAlmostEqual(stats["forwardedFps"], stats["sourceFps"], delta=2)
                else:
                    self.assertAlmostEqual(stats["forwardedFps"], limit, delta=5)
            rates.append(stats["forwardedFps"])
        self.assertTrue(all(a < b for a, b in zip(rates, rates[1:])), rates)
        self.assertEqual(self.source.accepted, 1)
        self.proxy.stop()
        self.assertEqual(self.proxy.sample_stats()["forwardedFps"], 0)
        self.assertEqual(self.proxy.sample_stats()["sourceFps"], 0)

    def test_fragmented_multipart_without_content_length(self):
        import io
        class Fragmented(io.BytesIO):
            def read1(self, size):
                return self.read(3)
        part = b"Content-Type: image/jpeg\r\n\r\n" + JPEG
        data = b"--quoted-boundary\r\n" + part + b"\r\n--quoted-boundary\r\n" + part + b"\r\n--quoted-boundary--\r\n"
        frames = list(multipart_parts(Fragmented(data), b"--quoted-boundary", threading.Event()))
        self.assertEqual(frames, [part, part])

    def test_non_mjpeg_response_is_rejected(self):
        url = self.proxy.prepare(self.source.url + "/not-mjpeg")
        with self.assertRaises(HTTPError) as error:
            urlopen(url, timeout=2)
        self.assertEqual(error.exception.code, 502)


if __name__ == "__main__":
    unittest.main()
