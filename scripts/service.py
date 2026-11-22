#!/usr/bin/env python3
"""Install our service and register it in the Moonraker service allowlist."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
UNIT = Path("/etc/systemd/system/KlipperScreenCam.service")
MARKER = "# Managed by KlipperScreenCam installer"


def quote(value):
    value = str(value)
    if any(character in value for character in ("\n", "\r", "\0")):
        raise ValueError("Newlines and NUL are not valid in service paths")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'


def unit_text(root, config, username, uid, home, ks_service="KlipperScreen.service"):
    # Values used unquoted as systemd identifiers are strictly constrained.
    import re
    if not re.fullmatch(r"[a-zA-Z0-9_.@-]+", username):
        raise ValueError("Unsupported service username")
    if ks_service != "none" and not re.fullmatch(r"[a-zA-Z0-9_.@-]+\.service", ks_service):
        raise ValueError("Invalid KlipperScreen service name")
    relationship = "After=network.target\n"
    if ks_service != "none":
        relationship += f"Wants={ks_service}\nAfter={ks_service}\nPartOf={ks_service}\n"
    return f"""{MARKER}
[Unit]
Description=KlipperScreenCam camera display
{relationship}
[Service]
Type=simple
User={username}
Environment={quote('HOME=' + str(home))}
Environment={quote('XDG_RUNTIME_DIR=/run/user/' + str(uid))}
Environment=PYTHONUNBUFFERED=1
ExecStart=:/usr/bin/python3 {quote(root / 'launcher.py')} --config {quote(config)}
Restart=on-failure
RestartSec=5
KillMode=control-group
TimeoutStopSec=15
UMask=0077

[Install]
WantedBy=multi-user.target
"""


def run(*command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True)


def managed_unit():
    if UNIT.is_symlink():
        raise RuntimeError(f"Refusing to modify a symlink: {UNIT}")
    if UNIT.exists() and MARKER not in UNIT.read_text():
        raise RuntimeError(f"Existing unit is not managed by this installer: {UNIT}")


def register_moonraker_service(data_dir):
    """Append only our service, preserving bytes and a first-change backup."""
    path = Path(data_dir) / "moonraker.asvc"
    if not path.parent.is_dir():
        raise ValueError(f"Moonraker data directory does not exist: {path.parent}")
    if path.is_symlink():
        raise RuntimeError(f"Refusing to modify a symlink: {path}")
    original = path.read_bytes() if path.exists() else b""
    if any(line.strip() == b"KlipperScreenCam" for line in original.splitlines()):
        return False
    if path.exists():
        backup = path.with_name(path.name + ".ksc-backup")
        try:
            with backup.open("xb") as stream:
                stream.write(original)
        except FileExistsError:
            pass  # Keep the original backup on repeated installation.
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    addition = (newline if original and not original.endswith(b"\n") else b"")
    addition += b"KlipperScreenCam" + newline
    with path.open("ab") as stream:
        stream.write(addition)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--config-dir", type=Path, default=Path.home() / "printer_data/config")
    parser.add_argument("--no-deps", action="store_true", help="Skip apt dependency installation")
    parser.add_argument("--enable", action="store_true", help="Enable and start the new service")
    parser.add_argument("--klipperscreen-service", default="KlipperScreen.service",
                        help="Use 'none' for an independently managed X11 session")
    parser.add_argument("--moonraker-data-dir", type=Path,
                        help="Moonraker data directory; defaults to parent of --config-dir")
    parser.add_argument("--skip-moonraker-registration", action="store_true",
                        help="Do not modify the Moonraker service allowlist")
    args = parser.parse_args()
    if sys.platform != "linux":
        raise RuntimeError("The installer supports Linux with apt/systemd only")
    if os.getuid() == 0:
        raise RuntimeError("Run as the regular printer user, not sudo/root. Sudo is requested only where needed.")
    import pwd
    managed_unit()
    if args.action == "uninstall":
        if not UNIT.exists():
            print("KlipperScreenCam service is not installed.")
            return 0
        run("sudo", "systemctl", "disable", "--now", UNIT.name)
        run("sudo", "rm", "--", UNIT)
        run("sudo", "systemctl", "daemon-reload")
        print("Service removed. Configuration, translations and source files were retained.")
        print("If no longer needed, remove only KlipperScreenCam from moonraker.asvc and restart Moonraker.")
        return 0

    config_dir = args.config_dir.expanduser().resolve()
    config = config_dir / "KlipperScreenCam.conf"
    account = pwd.getpwuid(os.getuid())
    unit = unit_text(ROOT, config, account.pw_name, account.pw_uid,
                     Path(account.pw_dir), args.klipperscreen_service)
    run("/usr/bin/python3", ROOT / "launcher.py", "--check-locales")
    if not args.no_deps:
        run("sudo", "apt-get", "update")
        run("sudo", "apt-get", "install", "--no-install-recommends", "-y",
            "python3-gi", "gir1.2-gtk-3.0", "gir1.2-webkit2-4.1",
            "fonts-noto-core", "fonts-noto-cjk")
    run("/usr/bin/python3", "-c",
        'import gi; gi.require_version("Gtk", "3.0"); gi.require_version("WebKit2", "4.1"); '
        'from gi.repository import Gtk, WebKit2')
    config_dir.mkdir(parents=True, exist_ok=True)
    if not config.exists():
        # Exclusive creation prevents accidental overwriting on repeated install.
        with config.open("x", encoding="utf-8") as stream:
            stream.write((ROOT / "config/KlipperScreenCam.conf").read_text(encoding="utf-8"))
        print("Created:", config)
    else:
        print("Keeping existing configuration:", config)
    run("/usr/bin/python3", ROOT / "launcher.py", "--config", config, "--check")
    if UNIT.exists():
        backup = UNIT.with_suffix(".service.ksc-backup")
        run("sudo", "cp", "-p", "--", UNIT, backup)
    with tempfile.TemporaryDirectory(prefix="klipperscreencam-install-") as temporary:
        staged = Path(temporary) / UNIT.name
        staged.write_text(unit, encoding="utf-8")
        run("systemd-analyze", "verify", staged)
        run("sudo", "install", "-m", "0644", "--", staged, UNIT)
    run("sudo", "systemctl", "daemon-reload")
    if not args.skip_moonraker_registration:
        data_dir = (args.moonraker_data_dir.expanduser().absolute()
                    if args.moonraker_data_dir else config_dir.parent)
        changed = register_moonraker_service(data_dir)
        print("Moonraker service allowlist:", data_dir / "moonraker.asvc",
              "(added)" if changed else "(already registered)")
        print("Restart the matching Moonraker service at a suitable time to load the allowlist.")
        print("  sudo systemctl restart moonraker  # adjust for a custom instance")
    if args.enable:
        run("sudo", "systemctl", "enable", "--now", UNIT.name)
    else:
        print("Installed, not started. After checking configuration and migration:")
        print("  sudo systemctl enable --now KlipperScreenCam")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print("Installation error:", error, file=sys.stderr)
        raise SystemExit(1)
