"""Configuration is deliberately independent of GTK and the target machine."""
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
import os
import re


@dataclass(frozen=True)
class Settings:
    path: Path
    moonraker_url: str
    web_url: str
    default_camera: str
    language: str
    ks_directory: Path
    ks_config: Path | None
    theme: str
    poll_seconds: int
    display: str
    xauthority: Path
    x: int
    y: int
    width: int
    height: int
    menu_width: int
    gear_size: int
    hide_cursor: bool
    hide_name_single: bool
    hardware_acceleration: str
    max_fps: int | None
    start_paused: bool
    retry_initial: int
    retry_max: int
    request_timeout: int


def load(path: Path) -> Settings:
    path = path.expanduser().resolve()
    parser = ConfigParser(interpolation=None)
    with path.open(encoding="utf-8-sig") as stream:
        parser.read_file(stream)

    allowed = {
        "main": {"moonraker_url", "web_url", "default_camera", "language",
                 "klipperscreen_directory", "klipperscreen_config", "theme",
                 "theme_poll_seconds"},
        "display": {"display", "xauthority", "x", "y", "width", "height",
                    "menu_min_width", "gear_size", "hide_cursor", "hide_name_single_camera",
                    "hardware_acceleration"},
        "stream": {"reconnect_initial_seconds", "reconnect_max_seconds",
                   "request_timeout_seconds", "start_paused", "max_fps"},
    }
    if parser.defaults():
        raise ValueError("[DEFAULT] is not supported")
    for section in parser.sections():
        if section not in allowed:
            raise ValueError(f"Unknown configuration section: {section}")
        unknown = set(parser[section]) - allowed[section]
        if unknown:
            raise ValueError(f"Unknown options in [{section}]: {sorted(unknown)}")

    def value(section, key, default):
        return parser.get(section, key, fallback=str(default)).strip()

    def integer(section, key, default, low, high):
        result = int(value(section, key, default))
        if not low <= result <= high:
            raise ValueError(f"{section}.{key} must be between {low} and {high}")
        return result

    def filesystem(raw):
        result = Path(os.path.expanduser(raw))
        return (result if result.is_absolute() else path.parent / result).resolve()

    def url(key, default):
        result = value("main", key, default).rstrip("/")
        parsed = urlsplit(result)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError(f"Invalid HTTP URL: main.{key}")
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError(f"Use a base URL without credentials/query: main.{key}")
        return result

    language = value("main", "language", "auto")
    theme = value("main", "theme", "auto")
    for key, entry in (("language", language), ("theme", theme)):
        if not re.fullmatch(r"[\w-]+", entry, flags=re.ASCII):
            raise ValueError(f"Invalid {key}: {entry}")
    custom_config = value("main", "klipperscreen_config", "")
    acceleration = value("display", "hardware_acceleration", "off").lower()
    if acceleration not in ("off", "auto", "on"):
        raise ValueError("display.hardware_acceleration must be off, auto or on")
    fps = value("stream", "max_fps", "15").lower()
    max_fps = None if fps == "unlimited" else integer("stream", "max_fps", 15, 1, 120)
    initial = integer("stream", "reconnect_initial_seconds", 2, 1, 300)
    maximum = integer("stream", "reconnect_max_seconds", 30, initial, 600)
    return Settings(
        path, url("moonraker_url", "http://127.0.0.1:7125"),
        url("web_url", "http://127.0.0.1"),
        value("main", "default_camera", ""), language,
        filesystem(value("main", "klipperscreen_directory", "~/KlipperScreen")),
        filesystem(custom_config) if custom_config else None, theme,
        integer("main", "theme_poll_seconds", 2, 1, 60),
        value("display", "display", ":0"),
        filesystem(value("display", "xauthority", "~/.Xauthority")),
        integer("display", "x", 1024, -32768, 32768),
        integer("display", "y", 0, -32768, 32768),
        integer("display", "width", 1024, 320, 8192),
        integer("display", "height", 600, 200, 8192),
        integer("display", "menu_min_width", 410, 200, 4096),
        integer("display", "gear_size", 88, 40, 200),
        parser.getboolean("display", "hide_cursor", fallback=True),
        parser.getboolean("display", "hide_name_single_camera", fallback=True),
        acceleration,
        max_fps,
        parser.getboolean("stream", "start_paused", fallback=False),
        initial, maximum,
        integer("stream", "request_timeout_seconds", 5, 1, 60),
    )
