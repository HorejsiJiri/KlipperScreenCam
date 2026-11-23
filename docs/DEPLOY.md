# Install KlipperScreenCam 0.3.0

[English](DEPLOY.md) · [Česky](DEPLOY.cs.md)

I run KlipperScreenCam as a separate service alongside KlipperScreen. My setup is a
Raspberry Pi 5 with Debian 13, X11 and two 1024 × 600 HDMI touch displays.
Run commands over SSH as the regular printer user who runs KlipperScreen.

## 1. Prepare the displays

Follow [the HDMI and touch guide](SECOND_DISPLAY.md) first if the extended desktop
is not configured. The installer preserves display modes and touch mappings; it
does not configure them. Keep existing camera streams working in Mainsail.

## 2. Extract and install

Copy `KlipperScreenCam-0.3.0.tar.gz` to the printer user's home directory.
If `~/KlipperScreenCam` already exists, follow [update and rollback](UPDATE.md)
instead of extracting over an unknown installation.

```bash
cd ~
tar -xzf KlipperScreenCam-0.3.0.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh
```

The installer installs dependencies, creates and validates the service, and preserves
an existing configuration. It does not enable or start the service by default.
The supported deployment runs from this directory; `pip install` is not required.

## 3. Configure

```bash
python3 launcher.py --list-cameras
nano ~/printer_data/config/KlipperScreenCam.conf
python3 launcher.py --check
```

Set `default_camera` in `[main]` to an exact Moonraker name or UID. Use a UID if the
camera may be renamed. Crowsnest device paths are not camera identifiers here.
The default window is at x=1024, y=0, width=1024, height=600. The default local limit
is 15 FPS. See [configuration](CONFIGURATION.md) for all settings.

If replacing my earlier shared startup viewer, follow [migration](MIGRATION.md)
before starting the new service. Do not run both camera viewers together.

## 4. Start and check

```bash
sudo systemctl start KlipperScreenCam
systemctl status KlipperScreenCam --no-pager
journalctl -u KlipperScreenCam -n 80 --no-pager
```

Check camera switching, touch input, video off/on, theme changes and simultaneous
Mainsail access. Then enable startup:

```bash
sudo systemctl enable KlipperScreenCam
```

## 5. Optional shared wake and sleep pause

```bash
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps --shared-wake
python3 launcher.py --check
```

Only after both commands succeed, restart both services at a suitable time outside a print:

```bash
sudo systemctl restart KlipperScreen
sudo systemctl restart KlipperScreenCam
```

Both restarts matter: KlipperScreen must load the wake notification code.
See [sleep and shared wake](RPI_SLEEP.md) for backups, supported source versions,
configuration and checks. A KlipperScreen update can overwrite this optional patch.

## 6. Moonraker and reboot

The installer registers the service in `moonraker.asvc`. Restart the matching
Moonraker service once outside a print to load the allowlist. See [service control](MOONRAKER.md).
Reboot the RPi when convenient and verify both displays, both touch inputs and sleep/wake.

Installer options include `--no-deps`, `--enable`, `--config-dir PATH`,
`--moonraker-data-dir PATH`, `--skip-moonraker-registration` and
`--klipperscreen-service none` for an independently managed X11 session.

To uninstall the service while retaining configuration, source and translations:

```bash
bash ~/KlipperScreenCam/scripts/uninstall.sh
```
