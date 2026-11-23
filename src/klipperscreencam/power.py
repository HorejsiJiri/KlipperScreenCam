"""Read X11 DPMS without changing its timers, and gate the local transport."""
import ctypes as C
import logging
import os
from pathlib import Path
import stat

LOG = logging.getLogger(__name__)


class DisplayPower:
    def __init__(self, stop_stream, notify):
        self.sleeping = False
        self.stop_stream = stop_stream
        self.notify = notify

    def update(self, awake):
        if awake is None:
            return False  # An unavailable query is not a wake event.
        sleeping = not awake
        if sleeping == self.sleeping:
            return False
        self.sleeping = sleeping
        if sleeping:
            self.stop_stream()  # Close real sockets before notifying WebKit.
        self.notify(sleeping)
        return True

    def permits_stream(self):
        return not self.sleeping


class DPMSMonitor:
    def __init__(self, display_name):
        self.display = None
        try:
            self.x11 = C.CDLL("libX11.so.6")
            self.ext = C.CDLL("libXext.so.6")
            self.x11.XOpenDisplay.argtypes = [C.c_char_p]
            self.x11.XOpenDisplay.restype = C.c_void_p
            self.x11.XCloseDisplay.argtypes = [C.c_void_p]
            self.x11.XCloseDisplay.restype = C.c_int
            self.ext.DPMSQueryExtension.argtypes = [C.c_void_p, C.POINTER(C.c_int), C.POINTER(C.c_int)]
            self.ext.DPMSQueryExtension.restype = C.c_int
            self.ext.DPMSCapable.argtypes = [C.c_void_p]
            self.ext.DPMSCapable.restype = C.c_int
            self.ext.DPMSInfo.argtypes = [C.c_void_p, C.POINTER(C.c_ushort), C.POINTER(C.c_ubyte)]
            self.ext.DPMSInfo.restype = C.c_int
            self.display = self.x11.XOpenDisplay(display_name.encode())
            if not self.display:
                raise OSError("Cannot open X11 display")
            event, error = C.c_int(), C.c_int()
            if (not self.ext.DPMSQueryExtension(self.display, C.byref(event), C.byref(error))
                    or not self.ext.DPMSCapable(self.display)):
                raise OSError("X11 display does not support DPMS")
            LOG.info("DPMS sleep monitoring enabled on %s", display_name)
        except (OSError, AttributeError) as error:
            self.close()
            LOG.warning("DPMS sleep monitoring unavailable: %s", error)

    def is_on(self):
        if not self.display:
            return None
        level, enabled = C.c_ushort(), C.c_ubyte()
        if not self.ext.DPMSInfo(self.display, C.byref(level), C.byref(enabled)):
            return None
        # With DPMS disabled the returned power level is undefined.
        return not enabled.value or level.value == 0

    def close(self):
        if self.display:
            self.x11.XCloseDisplay(self.display)
            self.display = None


class WakePipe:
    """One local notification FIFO; reading it never polls or launches commands."""
    def __init__(self, runtime_dir=None):
        runtime = Path(runtime_dir or os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
        directory = runtime / "KlipperScreenCam"
        directory.mkdir(mode=0o700, exist_ok=True)
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
            raise OSError("Unsafe wake notification directory")
        os.chmod(directory, 0o700)
        self.path = directory / "wake.fifo"
        try:
            os.mkfifo(self.path, 0o600)
        except FileExistsError:
            pass
        info = self.path.lstat()
        if not stat.S_ISFIFO(info.st_mode) or info.st_uid != os.getuid():
            raise OSError("Unsafe wake notification FIFO")
        os.chmod(self.path, 0o600)
        self.fd = os.open(self.path, os.O_RDWR | os.O_NONBLOCK)
        self.buffer = b""

    def read_wake(self):
        try:
            data = os.read(self.fd, 4096)
        except BlockingIOError:
            return False
        self.buffer += data
        lines = self.buffer.split(b"\n")
        self.buffer = lines.pop()[-64:]
        return any(line == b"wake" for line in lines)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
