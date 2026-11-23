# KlipperScreenCam

A standalone touch camera display for Klipper and Moonraker, styled to match KlipperScreen.
Keep printer controls on one HDMI screen and a selected camera on the other.

[Česky](README.cs.md) · [Second HDMI display and touch setup](docs/SECOND_DISPLAY.md) ·
[Deployment](docs/DEPLOY.md) · [Translations](docs/TRANSLATIONS.md)

**Version 0.3.0.**

I created KlipperScreenCam for my printer because I wanted KlipperScreen controls
on one display and a clear, switchable camera view on the other, while keeping
remote access through Mainsail. My setup uses a Raspberry Pi 5, Debian 13, X11
and two 1024 × 600 HDMI touch displays. The guides follow this setup.

## Features

- Existing HTTP MJPEG streams and camera names from Moonraker. No direct camera-device access.
- A fixed startup camera by exact name or UID, independent of the Mainsail web view.
- Full-window video preserving aspect ratio, with transparent name/settings overlays.
- A touch menu at the top-right edge, scrollable camera list and equally sized entries.
- Stop the local camera connection to reduce local work; a crossed-out camera shows “Video off” only after the Python host confirms shutdown.
  Selecting any camera, including the same one, starts a new stream connection.
- With one enabled camera, hide its name but keep the menu accessible for pause/resume.
- GTK-computed colors and SVG icons from the selected local KlipperScreen theme.
- Theme and language changes checked automatically, normally every two seconds.
- Editable JSON translations for all 32 locale variants in the recorded KlipperScreen snapshot.
- Arabic, Persian and Hebrew right-to-left menus; regional and legacy locale aliases.
- Reconnection after reported stream errors, with bounded retry backoff.
- A separate service, installer and uninstaller. Optional shared wake applies a backed-up KlipperScreen source patch.

## Requirements

- Linux with apt/systemd, X11, GTK 3 and WebKitGTK API 4.1.
- A working KlipperScreen installation and a readable local theme directory.
- Moonraker with cameras configured in Mainsail/Moonraker, using HTTP(S) MJPEG streams.
- Two displays and touch inputs already configured on the same X11 desktop.

The app does **not** configure HDMI modes or touch mapping. Follow the separate
[step-by-step display guide](docs/SECOND_DISPLAY.md) if needed. The tested example
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

If migrating from the earlier shared startup script, first follow
[migration instructions](docs/MIGRATION.md). Preserve HDMI and touch setup and disable
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

## Moonraker service control

The installer adds `KlipperScreenCam` to `<Moonraker data directory>/moonraker.asvc`
without duplicates or removing existing entries, keeping a first-change backup.
Restart the matching Moonraker service manually during initial setup.
The service can then be restarted using `POST /machine/services/restart` with
`{"service":"KlipperScreenCam"}`, subject to normal Moonraker authorization.
See the [step-by-step guide](docs/MOONRAKER.md). Use `--moonraker-data-dir PATH` for a custom data directory, or
`--skip-moonraker-registration` to leave the allowlist unchanged.

## Configure

[Complete configuration reference](docs/CONFIGURATION.md) · [Changelog](CHANGELOG.md)

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
pause_on_dpms = true
dpms_poll_seconds = 20

[stream]
max_fps = 15
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

KlipperScreen keeps control of blanking. With `pause_on_dpms = true` the viewer
closes its local stream after detecting X11 DPMS sleep, normally within 20 seconds.
The optional shared-wake integration sends an immediate wake notification and
closes KlipperScreen's black overlay. A software-only screensaver without DPMS
is not tracked. Follow [sleep and shared wake](docs/RPI_SLEEP.md).

WebRTC/HLS/RTSP, Wayland and direct `/dev/video*` access are not supported.
Reported stream failures trigger reconnect; a silent stall on an open HTTP connection may not
raise an image error. Reselecting the same camera forces a reconnect. Multiple viewers add
decoding/network load; measure it on your hardware. Menu geometry stays ours even when colors match a theme.
All locales/fonts, themes and failure scenarios have not been exhaustively tested on the target.

## Maintenance

```bash
sudo systemctl restart KlipperScreenCam
systemctl status KlipperScreenCam --no-pager
journalctl -u KlipperScreenCam -n 100 --no-pager
python3 -m unittest discover -s tests -v
bash scripts/uninstall.sh
```

Uninstall removes only our service, retaining config/source/translations.
See [update and rollback](docs/UPDATE.md), [test plan](docs/TESTING.md) and
[contribution guide](CONTRIBUTING.md). GitHub Actions runs checks, including real systemd validation on Linux.

## Project status

KlipperScreenCam is not an official KlipperScreen component. Theme SVG files are read from
your existing installation and are not redistributed here; bundled fallback icons are original.
I have not selected a project license yet. I keep detailed validation notes in RELEASE_CHECKS.md.

## Stream-off semantics

The Python host owns one cancellable upstream HTTP connection and exposes a random, single-use
loopback URL to WebKit. Video off closes the camera TCP socket and the local downstream socket.
It does not rely on removing img.src. Stale browser requests receive HTTP 410 and cannot restart
the camera. Switching cameras closes the previous connection. Other camera clients and Crowsnest
remain independent. The loopback transport adds a local relay, not another video decoder.

## Optional GPU rendering

Set `[display] hardware_acceleration = on` to request accelerated WebKit rendering,
`auto` for on-demand, or `off` for the original behavior. Missing values default to off.
This does not guarantee hardware MJPEG decoding. Compare CPU and smoothness on the target;
see [the acceleration guide](docs/ACCELERATION.md). Restart KlipperScreenCam after changes.

## Local FPS limit

Set `max_fps = 15` in `[stream]` (default 15; range 1–120 or `unlimited`). Complete compressed
frames are dropped without re-encoding before WebKit. The original upstream stream
is still read; Mainsail is unaffected. Restart the service after changing configuration.
I found both 15 FPS and 10 FPS smooth on my printer. Choose a limit that suits your view; I keep measurement details in [verification](docs/VERIFICATION.md).

The touch menu offers 10, 20, 30 FPS and Unlimited. Changes apply immediately,
without reconnecting or resuming paused video, and last until service restart.
Restart restores `max_fps` from configuration. A custom configured numeric limit is inserted as an additional sorted preset,
without duplicates. Numeric buttons have equal widths; Unlimited fills the rest
of the second row. The menu order is cameras, video toggle, frame-limit heading,
measured source/forwarded FPS, then preset buttons.
Unlimited forwards all available source frames and may increase CPU use.

## Display sleep and shared wake

I verified this setup on my Raspberry Pi 5, including a reboot. Touching either
screen wakes both displays. The local stream closes after DPMS sleep is detected
(default check interval: 20 seconds). A local FIFO wake notification resumes video
without waiting for that interval; manually paused video remains paused.

Set `pause_on_dpms = true` and `dpms_poll_seconds = 20` in `[display]`.
Install the optional integration with `--shared-wake`, then restart both services.
See the [step-by-step sleep/wake guide](docs/RPI_SLEEP.md).
KlipperScreen updates can overwrite this optional integration.
