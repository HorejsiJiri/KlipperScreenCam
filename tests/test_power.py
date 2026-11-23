import ctypes as C
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from klipperscreencam.power import DisplayPower, DPMSMonitor, WakePipe
from klipperscreencam.config import load
spec = importlib.util.spec_from_file_location("shared_wake", ROOT / "scripts/shared_wake.py")
wake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wake)


class PowerTests(unittest.TestCase):
    def test_sleep_closes_before_notification_and_unknown_never_wakes(self):
        events = []
        power = DisplayPower(lambda: events.append("closed"), lambda s: events.append(s))
        self.assertTrue(power.update(False))
        self.assertEqual(events, ["closed", True])
        self.assertFalse(power.permits_stream())
        self.assertFalse(power.update(None))
        self.assertFalse(power.update(False))
        self.assertEqual(events, ["closed", True])
        self.assertTrue(power.update(True))
        self.assertTrue(power.permits_stream())
        self.assertEqual(events, ["closed", True, False])

    def test_dpms_levels_and_disabled_level(self):
        monitor = DPMSMonitor.__new__(DPMSMonitor)
        monitor.display = 1
        monitor.ext = Mock()
        for level, enabled, expected in [(0, 1, True), (1, 1, False),
                                         (2, 1, False), (3, 1, False), (3, 0, True)]:
            def info(display, level_p, enabled_p):
                C.cast(level_p, C.POINTER(C.c_ushort))[0] = level
                C.cast(enabled_p, C.POINTER(C.c_ubyte))[0] = enabled
                return 1
            monitor.ext.DPMSInfo.side_effect = info
            self.assertEqual(monitor.is_on(), expected)
        monitor.ext.DPMSInfo.side_effect = None
        monitor.ext.DPMSInfo.return_value = 0
        self.assertIsNone(monitor.is_on())
        monitor.display = None
        self.assertIsNone(monitor.is_on())

    def test_unavailable_dpms_is_nonfatal(self):
        with patch("klipperscreencam.power.C.CDLL", side_effect=OSError("unavailable")):
            monitor = DPMSMonitor(":0")
        self.assertIsNone(monitor.is_on())
        monitor.close()

    def test_config_defaults_on_and_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.conf"
            path.write_text("[stream]\n")
            self.assertTrue(load(path).pause_on_dpms)
            self.assertEqual(load(path).dpms_poll_seconds, 20)
            path.write_text("[stream]\npause_on_dpms=false\ndpms_poll_seconds=30\n")
            self.assertFalse(load(path).pause_on_dpms)
            self.assertEqual(load(path).dpms_poll_seconds, 30)
            path.write_text("[stream]\ndpms_poll_seconds=0\n")
            with self.assertRaises(ValueError):
                load(path)

    def test_display_section_and_duplicate_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.conf"
            path.write_text("[display]\npause_on_dpms=false\ndpms_poll_seconds=30\n")
            self.assertFalse(load(path).pause_on_dpms)
            self.assertEqual(load(path).dpms_poll_seconds, 30)
            for key in ("pause_on_dpms", "dpms_poll_seconds"):
                value = "true" if key == "pause_on_dpms" else "20"
                path.write_text(f"[display]\n{key}={value}\n[stream]\n{key}={value}\n")
                with self.assertRaisesRegex(ValueError, "both"):
                    load(path)

    def test_verified_wake_patch_and_repeat_install(self):
        source = "class Screen:\n    def check_dpms_state(self):\n        state = functions.get_DPMS_state()\n        if not self.use_dpms:\n            return False\n" + wake.OLD
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "screen.py"
            path.write_text(source)
            saver = Path(directory) / "ks_includes/widgets/screensaver.py"
            saver.parent.mkdir(parents=True)
            saver.write_text("class ScreenSaver:\n    def close(self, widget=None):\n        self.screen.lock_screen.relock()\n")
            self.assertEqual(wake.apply(directory), [])
            self.assertEqual(path.read_text(), source)
            backups = wake.apply(directory, True)
            self.assertEqual(backups[0].read_text(), source)
            self.assertEqual(len(backups), 2)
            self.assertIn("KSC_WAKE_FIFO_V1", saver.read_text())
            self.assertIn(wake.NEW, path.read_text())
            self.assertEqual(wake.apply(directory, True), [])
            self.assertEqual(len(list(Path(directory).rglob("*.before-*"))), 2)

    def test_unknown_klipperscreen_is_not_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "screen.py"
            path.write_text("class Different: pass\n")
            with self.assertRaises(ValueError):
                wake.apply(directory, True)
            self.assertEqual(path.read_text(), "class Different: pass\n")
            self.assertFalse(list(Path(directory).glob("*.before-*")))


class WakeNotificationTests(unittest.TestCase):
    def test_partial_fifo_messages_and_unknown_commands(self):
        pipe = WakePipe.__new__(WakePipe)
        pipe.fd = 123
        pipe.buffer = b""
        with patch("klipperscreencam.power.os.read", side_effect=[b"wa", b"ke\nignored\n", b"ignored\n"]):
            self.assertFalse(pipe.read_wake())
            self.assertTrue(pipe.read_wake())
            self.assertFalse(pipe.read_wake())

    def test_both_patch_targets_validated_before_writing(self):
        source = "class Screen:\n    def check_dpms_state(self):\n        state = functions.get_DPMS_state()\n        if not self.use_dpms:\n            return False\n" + wake.OLD
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "screen.py"
            path.write_text(source)
            saver = Path(directory) / "ks_includes/widgets/screensaver.py"
            saver.parent.mkdir(parents=True)
            saver.write_text("class ChangedSaver: pass\n")
            with self.assertRaises(ValueError):
                wake.apply(directory, True)
            self.assertEqual(path.read_text(), source)
            self.assertFalse(list(Path(directory).rglob("*.before-*")))

    @unittest.skipUnless(sys.platform == "linux", "Native FIFO test requires Linux")
    def test_patched_close_delivers_wake_and_never_blocks_without_reader(self):
        with tempfile.TemporaryDirectory() as directory:
            pipe = WakePipe(directory)
            source = "class ScreenSaver:\n    def close(self, widget=None):\n        self.screen.lock_screen.relock()\n"
            patched, changed = wake.notified_source(source)
            self.assertTrue(changed)
            namespace = {}
            exec(patched, namespace)
            saver = namespace["ScreenSaver"]()
            saver.screen = Mock()
            with patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory}):
                saver.close()
                self.assertTrue(pipe.read_wake())
                pipe.close()
                saver.close()  # O_NONBLOCK + ENXIO is safely ignored.
