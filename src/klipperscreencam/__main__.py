import argparse
import json
import logging
import os
from pathlib import Path

from . import __version__
from .config import load
from .i18n import check_languages
from .moonraker import list_cameras

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description="KlipperScreenCam")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path,
                        default=Path.home() / "printer_data/config/KlipperScreenCam.conf")
    parser.add_argument("--check", action="store_true", help="Validate configuration without a GUI")
    parser.add_argument("--check-locales", action="store_true")
    parser.add_argument("--list-cameras", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        if args.check_locales:
            problems = check_languages(ROOT / "locales")
            for problem in problems:
                print(problem)
            if not problems:
                print("All language files are valid.")
            return int(bool(problems))
        settings = load(args.config)
        if args.check:
            print(f"Configuration OK: {settings.path}")
            return 0
        if args.list_cameras:
            for camera in list_cameras(settings):
                print(json.dumps({key: camera[key] for key in ("uid", "name", "supported")},
                                 ensure_ascii=False))
            return 0
        os.environ["DISPLAY"] = settings.display
        os.environ["XAUTHORITY"] = str(settings.xauthority)
        os.environ["GDK_BACKEND"] = "x11"
        from .app import run
        return run(settings, ROOT)
    except Exception:
        logging.getLogger(__name__).exception("KlipperScreenCam could not start")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
