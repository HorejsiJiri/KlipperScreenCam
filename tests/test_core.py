import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile
import unittest
import shutil
import subprocess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from klipperscreencam.config import load
from klipperscreencam.i18n import check_languages, load_language, read_language, html_language
from klipperscreencam.moonraker import normalize, startup_camera
from klipperscreencam.theme import klipperscreen_settings


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.config = self.directory / "KlipperScreenCam.conf"
        self.config.write_text("[main]\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def test_local_fps_configuration(self):
        self.config.write_text("[stream]\n")
        self.assertEqual(load(self.config).max_fps, 15)
        self.config.write_text("[stream]\nmax_fps=15\n")
        self.assertEqual(load(self.config).max_fps, 15)
        for invalid in ("0", "121", "-1", "abc"):
            self.config.write_text("[stream]\nmax_fps=" + invalid + "\n")
            with self.assertRaises(ValueError):
                load(self.config)

    def test_unlimited_fps_configuration(self):
        for value in ("unlimited", "UNLIMITED", " Unlimited "):
            self.config.write_text("[stream]\nmax_fps=" + value + "\n")
            self.assertIsNone(load(self.config).max_fps)

    def test_example_configuration(self):
        settings = load(ROOT / "config/KlipperScreenCam.conf")
        self.assertEqual((settings.width, settings.height), (1024, 600))

    def test_typo_in_configuration_is_rejected(self):
        self.config.write_text("[main]\ndefault_camer = Cam1\n")
        with self.assertRaisesRegex(ValueError, "Unknown"):
            load(self.config)

    def test_invalid_geometry_is_rejected(self):
        self.config.write_text("[display]\nwidth=0\n")
        with self.assertRaises(ValueError):
            load(self.config)

    def test_pause_and_single_camera_options(self):
        self.config.write_text("[display]\nhide_name_single_camera=false\n[stream]\nstart_paused=true\n")
        settings = load(self.config)
        self.assertFalse(settings.hide_name_single)
        self.assertTrue(settings.start_paused)

    def test_paths_are_relative_to_configuration(self):
        self.config.write_text("[main]\nklipperscreen_directory=../KS\n")
        self.assertEqual(load(self.config).ks_directory, (self.directory / "../KS").resolve())

    def test_old_configuration_keeps_acceleration_off(self):
        self.assertEqual(load(self.config).hardware_acceleration, "off")

    def test_acceleration_modes(self):
        for mode in ("off", "auto", "on", "ON"):
            with self.subTest(mode=mode):
                self.config.write_text("[display]\nhardware_acceleration=" + mode + "\n")
                self.assertEqual(load(self.config).hardware_acceleration, mode.lower())

    def test_invalid_acceleration_mode_is_rejected(self):
        self.config.write_text("[display]\nhardware_acceleration=enabled\n")
        with self.assertRaisesRegex(ValueError, "hardware_acceleration"):
            load(self.config)

    def test_invalid_url_rejected(self):
        self.config.write_text("[main]\nmoonraker_url=file:///etc/passwd\n")
        with self.assertRaises(ValueError):
            load(self.config)

    def test_retry_bounds_rejected(self):
        self.config.write_text("[stream]\nreconnect_initial_seconds=20\nreconnect_max_seconds=2\n")
        with self.assertRaises(ValueError):
            load(self.config)

    def test_repository_translations(self):
        self.assertEqual(check_languages(ROOT / "locales"), [])

    def test_czech_region_resolves(self):
        code, messages = load_language(ROOT / "locales", "cs_CZ.UTF-8")
        self.assertEqual(code, "cs")
        self.assertEqual(messages["menu_title"], "Kamery")

    def test_unknown_language_falls_back(self):
        code, _ = load_language(ROOT / "locales", "unknown")
        self.assertEqual(code, "en")

    def test_all_upstream_languages_are_present_and_selectable(self):
        upstream = json.loads((ROOT / "docs/UPSTREAM_LOCALES.json").read_text(encoding="utf-8"))
        expected = {entry["code"] for entry in upstream["locales"]}
        present = {path.stem for path in (ROOT / "locales").glob("*.json")}
        self.assertEqual(present, expected)
        for code in sorted(expected):
            with self.subTest(code=code):
                actual, messages = load_language(ROOT / "locales", code)
                self.assertEqual(actual, code)
                self.assertTrue(messages["menu_title"])

    def test_region_and_upstream_aliases(self):
        for requested, expected in {
            "pt_BR": "pt_BR", "PT-br.UTF-8": "pt_BR", "zh_CN": "zh_CN",
            "zh-TW": "zh_TW", "zh-Hant-HK": "zh_TW", "zh-Hans-CN": "zh_CN",
            "de_formal": "de_formal", "de-formal": "de_formal", "de_DE": "de",
            "ja_JP": "jp", "sr_RS": "rs", "cs_CZ": "cs",
        }.items():
            with self.subTest(requested=requested):
                self.assertEqual(load_language(ROOT / "locales", requested)[0], expected)

    def test_system_language_follows_os(self):
        with patch("klipperscreencam.i18n.locale.getlocale", return_value=("pt_BR", "UTF-8")):
            self.assertEqual(load_language(ROOT / "locales", "system_lang")[0], "pt_BR")

    def test_unspecified_ks_language_uses_system_language(self):
        self.assertEqual(klipperscreen_settings(load(self.config))["language"], "system_lang")

    def test_rtl_metadata_and_html_language_tags(self):
        for code in ("ar", "fa", "he"):
            self.assertEqual(load_language(ROOT / "locales", code)[1]["_meta"]["direction"], "rtl")
        self.assertEqual(html_language("jp"), "ja")
        self.assertEqual(html_language("rs"), "sr")
        self.assertEqual(html_language("de_formal"), "de")
        self.assertEqual(html_language("pt_BR"), "pt-BR")

    def test_invalid_direction_is_rejected(self):
        path = self.directory / "xx.json"
        path.write_text(json.dumps({"_meta": {"name": "Test", "code": "xx", "direction": "other"}}))
        with self.assertRaisesRegex(ValueError, "direction"):
            read_language(path)

    def test_missing_translations_use_english(self):
        (self.directory / "en.json").write_text((ROOT / "locales/en.json").read_text(encoding="utf-8"), encoding="utf-8")
        (self.directory / "xx.json").write_text(json.dumps({"_meta": {"code": "xx", "name": "Test"}, "menu_title": "Test"}))
        _, messages = load_language(self.directory, "xx")
        self.assertEqual(messages["menu_title"], "Test")
        self.assertEqual(messages["close_menu"], "Close menu")

    def test_duplicate_translation_keys_rejected(self):
        path = self.directory / "en.json"
        path.write_text('{"_meta":{"name":"English","code":"en"},"a":"1","a":"2"}')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            read_language(path)

    def test_camera_urls_use_web_server_not_api_port(self):
        cameras = normalize([{"uid": "1", "name": "A", "stream_url": "/webcam/?action=stream"}], "http://127.0.0.1")
        self.assertEqual(cameras[0]["url"], "http://127.0.0.1/webcam/?action=stream")

    def test_disabled_cameras_are_omitted(self):
        self.assertEqual(normalize([{"enabled": False, "stream_url": "/stream"}], "http://localhost"), [])

    def test_web_rtc_not_claimed_to_be_supported(self):
        cameras = normalize([{"uid": "1", "stream_url": "/webrtc", "service": "webrtc-camerastreamer"}], "http://localhost")
        self.assertFalse(cameras[0]["supported"])

    def test_startup_uid_survives_rename(self):
        cameras = [{"uid": "abc", "name": "Renamed"}, {"uid": "def", "name": "Other"}]
        self.assertEqual(startup_camera(cameras, "abc"), "abc")
        self.assertEqual(startup_camera(cameras, "Other"), "def")
        self.assertEqual(startup_camera(cameras, "missing"), "abc")

    def test_saved_klipperscreen_settings_override_manual_values(self):
        ks = self.directory / "KlipperScreen.conf"
        ks.write_text("[main]\ntheme=z-bolt\n#~# --- Do not edit below this line ---\n#~# [main]\n#~# theme=colorized\n#~# language=cs\n")
        settings = klipperscreen_settings(load(self.config))
        self.assertEqual(settings["theme"], "colorized")
        self.assertEqual(settings["language"], "cs")

    def test_include_settings_and_parent_precedence(self):
        (self.directory / "theme.conf").write_text("[main]\ntheme=colorized\nlanguage=cs\n")
        (self.directory / "KlipperScreen.conf").write_text("[include theme.conf]\n[main]\ntheme=z-bolt\n")
        settings = klipperscreen_settings(load(self.config))
        self.assertEqual(settings["theme"], "z-bolt")
        self.assertEqual(settings["language"], "cs")

    def test_service_unit_paths_are_quoted(self):
        spec = importlib.util.spec_from_file_location("ksc_service", ROOT / "scripts/service.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = module.unit_text(PurePosixPath("/home/test/My Project"), PurePosixPath("/home/test/config/a%p.conf"),
                                "test", 1000, PurePosixPath("/home/test"))
        self.assertNotIn("WorkingDirectory=", text)
        self.assertIn('ExecStart=:/usr/bin/python3 "/home/test/My Project/launcher.py"', text)
        self.assertIn("a%%p.conf", text)
        self.assertIn("PartOf=KlipperScreen.service", text)
        self.assertNotIn("camera-viewer.py", text)
        with self.assertRaises(ValueError):
            module.quote("bad\nExecStart=other")

    def test_custom_ks_config_is_preferred(self):
        (self.directory / "custom.conf").write_text("[main]\ntheme=material-dark\n")
        (self.directory / "KlipperScreen.conf").write_text("[main]\ntheme=z-bolt\n")
        self.config.write_text("[main]\nklipperscreen_config=custom.conf\n")
        self.assertEqual(klipperscreen_settings(load(self.config))["theme"], "material-dark")

    @unittest.skipUnless(sys.platform == "linux" and shutil.which("systemd-analyze"),
                         "Real systemd validation requires Linux")
    def test_generated_service_passes_systemd_validation(self):
        import os
        import pwd
        spec = importlib.util.spec_from_file_location("ksc_service_native", ROOT / "scripts/service.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        account = pwd.getpwuid(os.getuid())
        unit = self.directory / "KlipperScreenCam.service"
        unit.write_text(module.unit_text(ROOT, self.config, account.pw_name,
                                        account.pw_uid, Path(account.pw_dir)))
        stub = self.directory / "KlipperScreen.service"
        stub.write_text("[Service]\nType=simple\nExecStart=/usr/bin/true\n")
        result = subprocess.run(["systemd-analyze", "verify", str(unit), str(stub)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
