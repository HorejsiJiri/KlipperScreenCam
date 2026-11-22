# KlipperScreenCam

A standalone touch camera display for Klipper and Moonraker, styled to match KlipperScreen.
Keep printer controls on one HDMI screen and a selected camera on the other.

[Český návod](README.cs.md) · [Second HDMI display and touch setup](docs/SECOND_DISPLAY.cs.md) ·
[Deployment](docs/DEPLOY.cs.md) · [Translations](docs/TRANSLATIONS.cs.md)

**Version 0.2.0.** The standalone 0.1.x application was deployed on a Raspberry Pi 5,
Debian 13 (Trixie), X11 and two 1024 × 600 touch displays. The user confirmed video,
controls and automatic startup after the documented systemd fix.
This release adds the full upstream locale set; the new translations still need native-speaker review.
See [verification](docs/VERIFICATION.cs.md) and [release checks](RELEASE_CHECKS.md).

## Features

- Existing HTTP MJPEG streams and camera names from Moonraker. No direct camera-device access.
- A fixed startup camera by exact name or UID, independent of the Mainsail web view.
- Full-window video preserving aspect ratio, with transparent name/settings overlays.
- A touch menu at the top-right edge, scrollable camera list and equally sized entries.
- Pause the local video stream to reduce local work; a crossed-out camera shows “Video off”.
  Selecting any camera, including the same one, starts a new stream connection.
- With one enabled camera, hide its name but keep the menu accessible for pause/resume.
- GTK-computed colors and SVG icons from the selected local KlipperScreen theme.
- Theme and language changes checked automatically, normally every two seconds.
- Editable JSON translations for all 32 locale variants in the recorded KlipperScreen snapshot.
- Arabic, Persian and Hebrew right-to-left menus; regional and legacy locale aliases.
- Reconnection after reported stream errors, with bounded retry backoff.
- A separate service, installer and uninstaller; no edits to KlipperScreen source files.

## Requirements

- Linux with apt/systemd, X11, GTK 3 and WebKitGTK API 4.1.
- A working KlipperScreen installation and a readable local theme directory.
- Moonraker with cameras configured in Mainsail/Moonraker, using HTTP(S) MJPEG streams.
- Two displays and touch inputs already configured on the same X11 desktop.

The app does **not** configure HDMI modes or touch mapping. Follow the separate
[step-by-step display guide](docs/SECOND_DISPLAY.cs.md) if needed. The tested example
uses a 2048 × 600 desktop: printer screen at 0,0; camera screen at 1024,0.

## Install

Copy/clone the source tree to `~/KlipperScreenCam`, then run as the regular printer user:

```bash
cd ~/KlipperScreenCam
bash scripts/install.sh
nano ~/printer_data/config/KlipperScreenCam.conf
python3 launcher.py --check
python3 launcher.py --list-cameras
```

The installer installs dependencies, validates the generated systemd unit and preserves
an existing configuration. By default it does **not** start or enable the service.
It no longer generates the invalid quoted WorkingDirectory from the original 0.1.0 installer.

If migrating from the earlier shared startup script, first follow
[migration instructions](docs/MIGRATION.cs.md). Preserve HDMI and touch setup and disable
only the old camera process. Do not run both viewers at once.

For a pilot:

```bash
sudo systemctl start KlipperScreenCam
journalctl -u KlipperScreenCam -n 80 --no-pager
```

After verifying the display, touch controls and camera behavior:

```bash
sudo systemctl enable KlipperScreenCam
```

`bash scripts/install.sh --enable` installs and starts immediately. Use it only when ready.
`--config-dir PATH` selects another printer configuration directory. `--no-deps` skips apt.
For an independently managed X11 session, `--klipperscreen-service none` omits the service dependency.
Run the app from its checkout; `pip install` is not the supported deployment method.

## Configure

Edit `~/printer_data/config/KlipperScreenCam.conf` in Mainsail or a text editor.
The full example is [config/KlipperScreenCam.conf](config/KlipperScreenCam.conf).

```ini
[main]
default_camera = Cam2
language = auto
theme = auto

[display]
x = 1024
y = 0
width = 1024
height = 600
hide_name_single_camera = true

[stream]
start_paused = false
```

`default_camera` accepts the **exact Moonraker/Mainsail camera name or its UID**.
A UID survives renaming; list both using `python3 launcher.py --list-cameras` on the printer host.
Do not put the Crowsnest `device: /dev/v4l/by-path/...` path here: it identifies a physical
capture device, not the configured stream. An empty/missing/disabled startup choice falls
back to the first enabled camera. Runtime selection never rewrites the startup choice.

Restart the service after editing main configuration or changing the camera list.
Theme, selected language and translation-file edits are picked up automatically.
The viewer reads camera metadata only; it does not change camera configuration or Mainsail selection.

## Languages

```text
ar bg cs da de de_formal en es et fa fr he hr hu it jp ko lt nl pl
pt pt_BR rs ru sk sl sv tr uk vi zh_CN zh_TW
```

Each language has a UTF-8 JSON file in `locales/`. Copy en.json, translate values and validate:

```bash
python3 launcher.py --check-locales
```

The language identifiers come from the [official upstream locale tree](https://github.com/KlipperScreen/KlipperScreen/tree/023f604cb35215098aebe175425de96e05791d96/ks_includes/locales).
The snapshot is recorded in [docs/UPSTREAM_LOCALES.json](docs/UPSTREAM_LOCALES.json).
Our 30 new translations are independently prepared AI-assisted drafts, not imported or endorsed
upstream translations. Native-speaker corrections are welcome. Missing strings fall back to English.
The installer includes Noto core/CJK fonts for minimal systems.

## Display blanking and limitations

The app leaves X11 DPMS and blanking to the existing system/KlipperScreen setup.
It does not disable DPMS, and a software-only KlipperScreen screensaver does not automatically
cover this separate window. DPMS power-off alone does not pause video decoding;
use the menu's video-off action for that. Automatic pause based on DPMS is not implemented.

WebRTC/HLS/RTSP, Wayland and direct `/dev/video*` access are not supported.
Reported stream failures trigger reconnect; a silent stall on an open HTTP connection may not
raise an image error. Reselecting the same camera forces a reconnect. Multiple viewers add
decoding/network load; measure it on your hardware. Menu geometry stays ours even when colors match a theme.
Native GTK/WebKitGTK, fonts and new locale rendering still need target testing for this release.

## Maintenance

```bash
sudo systemctl restart KlipperScreenCam
systemctl status KlipperScreenCam --no-pager
journalctl -u KlipperScreenCam -n 100 --no-pager
python3 -m unittest discover -s tests -v
bash scripts/uninstall.sh
```

Uninstall removes only our service, retaining config/source/translations.
See [update and rollback](docs/UPDATE.cs.md), [test plan](docs/TESTING.cs.md) and
[contribution guide](CONTRIBUTING.md). GitHub Actions runs checks, including real systemd validation on Linux.

## Project status

KlipperScreenCam is not an official KlipperScreen component. Theme SVG files are read from
the user's existing installation and are not redistributed here; bundled fallback icons are original.
The project owner's license choice is pending. No repository has been published automatically.
