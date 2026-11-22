"""GTK/WebKit host. Moonraker is read-only; camera changes stay local."""
import fcntl
import hashlib
import json
import logging
import os
from pathlib import Path
import signal
import threading
import time

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gtk, GLib, WebKit2

from .i18n import load_language, html_language
from .moonraker import list_cameras, startup_camera
from .theme import klipperscreen_settings, theme_directory, icon_data, palette
from .stream import StreamProxy

LOG = logging.getLogger(__name__)


class Viewer(Gtk.Window):
    def __init__(self, settings, root):
        super().__init__(title="KlipperScreenCam")
        self.settings, self.root = settings, root
        self.ready = False
        self.loading = False
        self.stopped = False
        self.cameras = []
        self.streams = StreamProxy(timeout=settings.request_timeout, max_fps=settings.max_fps)
        self.stream_generation = -1
        self.appearance_signature = None
        self.messages = {}
        self.set_decorated(False)
        self.set_default_size(settings.width, settings.height)
        self.set_resizable(False)
        self.move(settings.x, settings.y)
        self.connect("destroy", self.close)
        self.manager = WebKit2.UserContentManager()
        self.manager.connect("script-message-received::ksc", self.message)
        self.manager.register_script_message_handler("ksc")
        self.web = WebKit2.WebView(user_content_manager=self.manager)
        acceleration = {
            "off": WebKit2.HardwareAccelerationPolicy.NEVER,
            "auto": WebKit2.HardwareAccelerationPolicy.ON_DEMAND,
            "on": WebKit2.HardwareAccelerationPolicy.ALWAYS,
        }[settings.hardware_acceleration]
        self.web.get_settings().set_hardware_acceleration_policy(acceleration)
        LOG.info("WebKit hardware acceleration requested: %s", settings.hardware_acceleration)
        self.web.connect("context-menu", lambda *_: True)
        self.web.connect("load-changed", self.loaded)
        self.web.connect("web-process-terminated", self.web_terminated)
        self.add(self.web)
        self.show_all()
        self.move(settings.x, settings.y)
        self.web.load_html((root / "web/index.html").read_text(encoding="utf-8"),
                           settings.web_url + "/")
        GLib.timeout_add_seconds(settings.poll_seconds, self.update_appearance)
        GLib.timeout_add_seconds(2, self.update_stream_stats)

    def close(self, *_):
        if self.stopped:
            return
        self.stopped = True
        self.streams.close()
        Gtk.main_quit()

    def javascript(self, function, data):
        if self.stopped or not self.ready:
            return
        script = function + "(" + json.dumps(data, ensure_ascii=True) + ");"
        self.web.run_javascript(script, None, self.javascript_finished, None)

    def javascript_finished(self, web, result, _data):
        try:
            web.run_javascript_finish(result)
        except GLib.Error as error:
            LOG.warning("UI update failed: %s", error.message)

    def loaded(self, _web, event):
        if event == WebKit2.LoadEvent.STARTED:
            self.ready = False
            self.stream_generation = -1
            self.streams.stop()
        elif event == WebKit2.LoadEvent.FINISHED:
            self.ready = True
            self.appearance_signature = None
            self.javascript("KSC.configure", {
                "menuWidth": self.settings.menu_width,
                "gearSize": self.settings.gear_size,
                "hideCursor": self.settings.hide_cursor,
                "hideNameSingle": self.settings.hide_name_single,
                "startPaused": self.settings.start_paused,
                "maxFps": self.streams.max_fps,
                "configuredMaxFps": self.settings.max_fps,
                "retryInitial": self.settings.retry_initial,
                "retryMax": self.settings.retry_max,
            })
            self.update_appearance()
            self.load_cameras()

    def update_stream_stats(self):
        if self.stopped:
            return False
        stats = self.streams.sample_stats()
        self.javascript("KSC.setStreamStats", stats)
        return True

    def web_terminated(self, _web, reason):
        LOG.error("Web renderer exited (%s); reloading", reason)
        self.streams.stop()
        self.ready = False
        GLib.timeout_add_seconds(3, self.reload_web)

    def reload_web(self):
        if not self.stopped:
            self.web.reload()
        return False

    def message(self, _manager, result):
        try:
            data = json.loads(result.get_js_value().to_string())
            if data.get("action") == "stream":
                generation = data.get("generation")
                if (type(generation) is not int or not 0 <= generation <= 2**53
                        or generation < self.stream_generation):
                    return
                self.stream_generation = generation
                uid = data.get("uid")
                if uid is None:
                    self.streams.stop()
                    self.javascript("KSC.streamStopped", {"generation": generation})
                    return
                camera = next((camera for camera in self.cameras
                               if camera["uid"] == uid and camera["supported"]), None)
                if camera is None:
                    self.streams.stop()
                    self.javascript("KSC.streamFailed", {"generation": generation})
                    return
                url = self.streams.prepare(camera["url"])
                self.javascript("KSC.streamReady", {"generation": generation, "url": url})
            elif data.get("action") == "fps":
                value = data.get("value")
                if value is not None and (type(value) is not int or value not in (10, 20, 30, self.settings.max_fps)):
                    raise ValueError("Invalid display FPS choice")
                if "value" not in data:
                    raise ValueError("Missing display FPS choice")
                self.streams.set_max_fps(value)
                self.javascript("KSC.setFps", {"value": value})
                LOG.info("Local FPS limit: %s", "unlimited" if value is None else value)
            elif data.get("action") == "selected":
                uid = data.get("uid")
                if any(camera["uid"] == uid for camera in self.cameras):
                    LOG.info("Camera selected: %s", uid)
        except (ValueError, AttributeError):
            LOG.warning("Ignored invalid UI message")

    def load_cameras(self):
        if self.loading or self.stopped:
            return False
        self.loading = True

        def worker():
            try:
                cameras, error = list_cameras(self.settings), None
            except Exception as caught:
                cameras, error = None, type(caught).__name__
            GLib.idle_add(self.show_cameras, cameras, error)

        threading.Thread(target=worker, daemon=True).start()
        return False

    def show_cameras(self, cameras, error):
        self.loading = False
        if self.stopped:
            return False
        if error:
            LOG.warning("Moonraker camera list failed: %s; retrying", error)
            self.javascript("KSC.error", "server_unavailable")
            GLib.timeout_add_seconds(10, self.load_cameras)
        elif self.ready:
            self.cameras = cameras
            preferred = startup_camera(cameras, self.settings.default_camera)
            if self.settings.default_camera and not any(
                self.settings.default_camera in (camera["uid"], camera["name"])
                for camera in cameras
            ):
                LOG.warning("Configured startup camera is absent/disabled; using first camera")
            self.javascript("KSC.setCameras", {"cameras": cameras, "preferred": preferred})
        return False

    def update_appearance(self):
        if self.stopped:
            return False
        if not self.ready:
            return True
        try:
            ks = klipperscreen_settings(self.settings)
            language = (ks.get("language", "en") if self.settings.language == "auto"
                        else self.settings.language)
            code, messages = load_language(self.root / "locales", language)
            theme = ks.get("theme", "z-bolt") if self.settings.theme == "auto" else self.settings.theme
            directory = theme_directory(self.settings, theme)
            icons = {name: icon_data(directory, name, self.root / "assets")
                     for name in ("settings", "camera")}
            source = (directory / "style.css").read_text(encoding="utf-8")
            signature = (theme, source, code, json.dumps(messages, sort_keys=True),
                         tuple(icons.items()))
            if signature != self.appearance_signature:
                colors = palette(directory)
                self.javascript("KSC.setAppearance", {
                    "colors": colors, "icons": icons, "messages": messages,
                    "language": html_language(code),
                })
                self.messages = messages
                self.set_title("KlipperScreenCam — " + messages["window_title"])
                self.appearance_signature = signature
                LOG.info("Appearance updated: theme=%s language=%s", theme, code)
        except Exception:
            LOG.exception("Could not update appearance; keeping the previous appearance")
            # A missing theme must not prevent translations or camera playback.
            if not self.messages:
                _, messages = load_language(self.root / "locales", "en")
                fallback = self.root / "assets"
                self.javascript("KSC.setAppearance", {
                    "messages": messages,
                    "language": "en",
                    "icons": {name: icon_data(fallback, name, fallback)
                              for name in ("settings", "camera")},
                })
                self.messages = messages
        return True


def run(settings, root):
    # An independent service may start before KlipperScreen's X server is ready.
    for _ in range(30):
        success, _args = Gtk.init_check([])
        if success:
            break
        time.sleep(1)
    else:
        raise RuntimeError("X11 is not ready. Check DISPLAY, XAUTHORITY and KlipperScreen.")
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "KlipperScreenCam"
    cache.mkdir(parents=True, exist_ok=True)
    identity = f"{settings.display}:{settings.x}:{settings.y}"
    lock_path = cache / (hashlib.sha256(identity.encode()).hexdigest()[:16] + ".lock")
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            LOG.error("Another KlipperScreenCam is already running at this position")
            return 1
        viewer = Viewer(settings, root)
        signal.signal(signal.SIGTERM, lambda *_: viewer.close())
        signal.signal(signal.SIGINT, lambda *_: viewer.close())
        Gtk.main()
    return 0
