"""Read KlipperScreen settings and ask GTK for computed theme colors."""
from configparser import ConfigParser
from pathlib import Path
import base64
import glob
import logging
import re

LOG = logging.getLogger(__name__)


def klipperscreen_settings(settings):
    result = {"theme": "z-bolt", "language": "system_lang"}

    def read(path, seen):
        path = Path(path).resolve()
        if not path.is_file() or path in seen:
            return
        seen.add(path)
        regular, saved = [], []
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("#~#"):
                line = line[3:].lstrip()
                if not line.startswith("---"):
                    saved.append(line)
            else:
                regular.append(line)
        for lines in (regular, saved):
            parser = ConfigParser(interpolation=None, strict=False)
            parser.read_string("\n".join(lines))
            for section in parser.sections():
                if section.startswith("include "):
                    pattern = str(path.parent / section[8:].strip())
                    for child in sorted(glob.glob(pattern)):
                        read(child, seen)
            if parser.has_section("main"):
                result.update(dict(parser.items("main")))

    read(settings.ks_directory / "config/defaults.conf", set())
    candidates = [settings.ks_config] if settings.ks_config else [
        settings.path.parent / "KlipperScreen.conf",
        Path.home() / "printer_data/config/KlipperScreen.conf",
        Path.home() / ".config/KlipperScreen/KlipperScreen.conf",
        settings.ks_directory / "KlipperScreen.conf",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            read(candidate, set())
            break
    return result


def theme_directory(settings, selected):
    if not re.fullmatch(r"[\w-]+", selected, flags=re.ASCII):
        raise ValueError("Invalid KlipperScreen theme name")
    path = settings.ks_directory / "styles" / selected
    if not (path / "style.css").is_file():
        raise FileNotFoundError(f"KlipperScreen theme not found: {path}")
    return path


def icon_data(directory, name, fallback):
    path = directory / "images" / (name + ".svg")
    if not path.is_file():
        path = fallback / (name + ".svg")
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def palette(directory):
    # Imported only in GUI mode; headless configuration/locale tests need no GTK.
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    provider = Gtk.CssProvider()
    provider.load_from_path(str(directory / "style.css"))
    measurement = Gtk.CssProvider()
    measurement.load_from_data(b"* { transition: none; background-image: none; }")
    window = Gtk.OffscreenWindow()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    window.add(box)
    label = Gtk.Label(label="Camera")
    box.add(label)
    buttons = []
    for number in range(1, 5):
        button = Gtk.Button(label="Camera")
        button.get_style_context().add_class(f"color{number}")
        box.add(button)
        buttons.append(button)
    active = Gtk.Button(label="Selected")
    active.get_style_context().add_class("active")
    box.add(active)
    menu = Gtk.Menu()
    for widget in [window, box, label, menu, active, *buttons]:
        context = widget.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 100)
        context.add_provider(measurement, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 101)
    window.show_all()
    normal = Gtk.StateFlags.NORMAL

    def background(widget, fallback):
        color = widget.get_style_context().get_background_color(normal)
        return color if color.alpha > 0 else fallback

    def border(widget, fallback):
        color = widget.get_style_context().get_property("border-bottom-color", normal)
        return color if color is not None and color.alpha > 0 else fallback

    try:
        foreground = label.get_style_context().get_color(normal)
        window_bg = background(window, foreground)
        result = {
            "bg": background(menu, window_bg).to_string(),
            "text": foreground.to_string(),
            "active": background(active, window_bg).to_string(),
            "lines": border(menu, foreground).to_string(),
        }
        for number, button in enumerate(buttons, 1):
            result[f"color{number}"] = border(button, foreground).to_string()
            result[f"button{number}"] = background(button, window_bg).to_string()
        return result
    finally:
        menu.destroy()
        window.destroy()
