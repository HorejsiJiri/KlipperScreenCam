"""A cancellable, single-consumer MJPEG transport owned by the application.

WebKit receives only an ephemeral loopback URL. It cannot keep reading an upstream
camera after stop(), even if removing an <img> fails to cancel its HTTP request.
"""
from dataclasses import dataclass, field
import base64
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
from email.message import Message
import time
import secrets
import socket
import threading
from urllib.parse import urljoin, urlsplit, unquote

LOG = logging.getLogger(__name__)


def close_socket(connection):
    try:
        connection.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        connection.close()
    except OSError:
        pass


@dataclass
class Session:
    url: str
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    cancelled: threading.Event = field(default_factory=threading.Event)
    lock: threading.Lock = field(default_factory=threading.Lock)
    sockets: list = field(default_factory=list)
    claimed: bool = False
    bytes_forwarded: int = 0
    frames_received: int = 0
    frames_forwarded: int = 0

    def register(self, connection):
        with self.lock:
            active = not self.cancelled.is_set()
            if active:
                self.sockets.append(connection)
        if not active:
            close_socket(connection)
        return active

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            connections = self.sockets[:]
            self.sockets.clear()
        # Close both TCP directions, not just the image element in the renderer.
        for connection in connections:
            close_socket(connection)


class StreamProxy:
    def __init__(self, timeout=5, max_fps=15):
        self.set_max_fps(max_fps)
        self.timeout = timeout
        self.lock = threading.Lock()
        self.current = None
        self.last_sample = None
        self.closed = False
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *_):
                pass  # Do not put secret loopback tokens or camera URLs in logs.

            def do_GET(self):
                session = owner.claim(self.path)
                if session is None:
                    self.send_error(410)
                    return
                if not session.register(self.connection):
                    return
                owner.forward(self, session)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.1}, daemon=True)
        self.thread.start()

    def set_max_fps(self, value):
        if value is not None and (type(value) is not int or not 1 <= value <= 120):
            raise ValueError("max_fps must be an integer from 1 to 120 or None (unlimited)")
        # Scalar assignment is atomic; the relay takes a snapshot for each frame.
        self.max_fps = value

    def sample_stats(self):
        """Rates measured from actual complete source and forwarded MJPEG parts."""
        now = time.monotonic()
        with self.lock:
            session = self.current
            if session is None or session.cancelled.is_set():
                self.last_sample = None
                return {"sourceFps": 0.0, "forwardedFps": 0.0, "maxFps": self.max_fps}
            received, forwarded = session.frames_received, session.frames_forwarded
            previous = self.last_sample
            self.last_sample = (session, now, received, forwarded)
        source_fps = forwarded_fps = 0.0
        if previous and previous[0] is session and now > previous[1]:
            elapsed = now - previous[1]
            source_fps = (received - previous[2]) / elapsed
            forwarded_fps = (forwarded - previous[3]) / elapsed
        return {"sourceFps": round(source_fps, 1),
                "forwardedFps": round(forwarded_fps, 1), "maxFps": self.max_fps}

    def prepare(self, url):
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("Only HTTP(S) camera streams can be proxied")
        self.stop()
        with self.lock:
            if self.closed:
                raise RuntimeError("Stream transport is closed")
            self.current = Session(url)
            token = self.current.token
        return f"http://127.0.0.1:{self.server.server_port}/stream/{token}"

    def claim(self, path):
        with self.lock:
            session = self.current
            if (session is None or session.cancelled.is_set() or session.claimed
                    or path != "/stream/" + session.token):
                return None
            session.claimed = True
            return session

    def stop(self):
        with self.lock:
            session, self.current = self.current, None
        if session is not None:
            session.cancel()
            LOG.info("Local camera connection closed; forwarded_bytes=%d", session.bytes_forwarded)

    def close(self):
        with self.lock:
            self.closed = True
        self.stop()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def forward(self, handler, session):
        connection = response = None
        headers_sent = False
        try:
            url = session.url
            for redirect in range(4):
                if session.cancelled.is_set():
                    return
                parsed = urlsplit(url)
                if parsed.scheme not in ("http", "https") or not parsed.hostname:
                    raise ValueError("Invalid stream redirect")
                cls = (http.client.HTTPSConnection if parsed.scheme == "https"
                       else http.client.HTTPConnection)
                connection = cls(parsed.hostname, parsed.port, timeout=self.timeout)
                connection.connect()
                # Capture the socket before HTTPResponse can detach it on Connection: close.
                if not session.register(connection.sock):
                    return
                if session.cancelled.is_set():
                    return
                target = parsed.path or "/"
                if parsed.query:
                    target += "?" + parsed.query
                headers = {"Accept": "multipart/x-mixed-replace, image/jpeg", "Connection": "close"}
                if parsed.username is not None:
                    credentials = unquote(parsed.username) + ":" + unquote(parsed.password or "")
                    headers["Authorization"] = "Basic " + base64.b64encode(credentials.encode()).decode()
                connection.request("GET", target, headers=headers)
                response = connection.getresponse()
                if response.status not in (301, 302, 303, 307, 308):
                    break
                location = response.getheader("Location")
                response.close()
                connection.close()
                if not location or redirect == 3:
                    raise ValueError("Invalid or excessive stream redirects")
                url = urljoin(url, location)
            if response.status != 200:
                raise ValueError("Camera returned a non-success HTTP status")
            content_type = response.getheader("Content-Type", "")
            if not content_type.lower().startswith("multipart/x-mixed-replace"):
                raise ValueError("Camera response is not a multipart MJPEG stream")
            metadata = Message()
            metadata["Content-Type"] = content_type
            boundary = metadata.get_param("boundary")
            if not boundary or len(boundary) > 200:
                raise ValueError("Missing or invalid MJPEG boundary")
            delimiter = b"--" + boundary.encode("ascii")
            if session.cancelled.is_set():
                return
            handler.send_response(200)
            handler.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            handler.send_header("Cache-Control", "no-store, no-cache")
            handler.send_header("Connection", "close")
            handler.send_header("X-Content-Type-Options", "nosniff")
            handler.end_headers()
            headers_sent = True
            next_frame = 0.0
            previous_limit = self.max_fps
            for part in multipart_parts(response, delimiter, session.cancelled):
                session.frames_received += 1
                now = time.monotonic()
                limit = self.max_fps
                if limit != previous_limit:
                    next_frame = 0.0
                    previous_limit = limit
                if limit is not None and now < next_frame:
                    continue
                # Drop complete frames; never sleep or queue old frames to limit FPS.
                chunk = b"--frame\r\n" + part + b"\r\n"
                handler.wfile.write(chunk)
                handler.wfile.flush()
                session.bytes_forwarded += len(chunk)
                session.frames_forwarded += 1
                if limit is None:
                    continue
                interval = 1.0 / limit
                if next_frame == 0.0:
                    next_frame = now + interval
                else:
                    # Keep cadence despite small arrival jitter; skip missed slots.
                    next_frame += (int((now - next_frame) / interval) + 1) * interval
        except (OSError, ValueError, http.client.HTTPException):
            if not session.cancelled.is_set():
                LOG.warning("Camera transport failed; reconnect can be requested by the UI")
                if not headers_sent:
                    try:
                        handler.send_error(502)
                    except OSError:
                        pass
        finally:
            session.cancel()
            if response is not None:
                response.close()
            if connection is not None:
                connection.close()


def multipart_parts(response, delimiter, cancelled):
    """Read bounded multipart parts, including streams without Content-Length.

    Keep one compressed frame at most. JPEG data is never decoded or re-encoded.
    A delimiter must start on its own line, as required by multipart MIME.
    """
    buffer = bytearray()
    marker = b"\r\n" + delimiter
    started = False
    while not cancelled.is_set():
        chunk = response.read1(65536)
        if not chunk or cancelled.is_set():
            return
        buffer.extend(chunk)
        while True:
            if not started:
                offset = buffer.find(delimiter)
                if offset < 0:
                    break
                del buffer[:offset + len(delimiter)]
                started = True
            offset = buffer.find(marker)
            if offset < 0:
                break
            part = bytes(buffer[:offset])
            del buffer[:offset + len(marker)]
            if part.startswith(b"\r\n"):
                part = part[2:]
            if b"\r\n\r\n" not in part:
                raise ValueError("Invalid multipart frame headers")
            yield part
            if buffer.startswith(b"--"):
                return
        if len(buffer) > 16 * 1024 * 1024:
            raise ValueError("MJPEG frame exceeds 16 MiB limit")
