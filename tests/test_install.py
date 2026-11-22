"""Moonraker allowlist preservation and repeated installation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ksc_install", ROOT / "scripts/service.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class AllowlistTests(unittest.TestCase):
    def test_preserves_existing_services_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "moonraker.asvc"
            original = b"# custom\r\nKlipperScreen\r\ncrowsnest"
            path.write_bytes(original)
            self.assertTrue(installer.register_moonraker_service(directory))
            expected = original + b"\r\nKlipperScreenCam\r\n"
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(path.with_name(path.name + ".ksc-backup").read_bytes(), original)
            self.assertFalse(installer.register_moonraker_service(directory))
            self.assertEqual(path.read_bytes(), expected)

    def test_creates_missing_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(installer.register_moonraker_service(directory))
            self.assertEqual((Path(directory) / "moonraker.asvc").read_bytes(), b"KlipperScreenCam\n")

    def test_missing_data_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                installer.register_moonraker_service(Path(directory) / "missing")

    def test_existing_backup_is_kept(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "moonraker.asvc"
            path.write_bytes(b"crowsnest\n")
            backup = Path(directory) / "moonraker.asvc.ksc-backup"
            backup.write_bytes(b"original backup")
            installer.register_moonraker_service(directory)
            self.assertEqual(backup.read_bytes(), b"original backup")
