# Changelog

Notable changes to KlipperScreenCam are recorded here. Versions use MAJOR.MINOR.PATCH.
The initial development iterations are consolidated into the first public release below.
Future releases get their own dated entry; published release entries are retained.

## 0.3.0 — 2026-11-22 

First public release baseline. The revised menu awaits target-device validation.

### Features

- Revised menu order: cameras, red icon video toggle, frame-limit heading, measured
  FPS and preset buttons. Custom configured limits become sorted, deduplicated
  buttons; Unlimited fills the remaining second-row space. Labels cover 32 locales.

- Live source and forwarded FPS counters in the menu, measured from complete
  MJPEG frames over two-second sampling intervals; these are not rendered FPS.
- Real-stream tests verify 10/20/30/unlimited changes on the same active connection.

- Installer registers its service in moonraker.asvc without duplicates, preserves
  existing services and a first-change backup, and leaves Moonraker restart manual.

- Standalone second-display camera viewer for Klipper and Moonraker, with its own
  systemd service, installer and printer configuration file.
- Camera names and streams from Moonraker; fixed startup camera by exact name or UID,
  independent of the Mainsail selection.
- Full-window MJPEG video, transparent overlays and a scrollable touch camera menu.
- Automatic KlipperScreen theme colors, SVG icons and language selection.
- Editable JSON translations for 32 language variants, with RTL support.
- Video off actually closes the local camera connection. Selecting a camera resumes it.
- Configurable local frame limit: `[stream] max_fps = 15` by default, range 1–120 or `unlimited`.
  Touch-menu presets: 10, 20, 30 FPS and Unlimited; live changes do not reconnect
  or resume paused video. Restart restores the configured startup limit.
  New labels are provided in all 32 locale files.
  Complete frames are dropped before WebKit without re-encoding; upstream camera
  traffic and other clients are unaffected.
- Optional WebKit rendering policy: `[display] hardware_acceleration = off/auto/on`.
  The default is off; this does not guarantee hardware MJPEG decoding.
- Step-by-step documentation for installation, two HDMI touch displays, configuration,
  Moonraker service control and translations; automated core and browser checks.

### Verified deployment

- The preceding 0.2.3 version: user-confirmed video, touch controls and automatic startup on Raspberry Pi 5,
  Debian 13, X11 and two 1024 × 600 HDMI touch displays.
- Actual stream closure confirmed with connection logs and socket checks.
- User-confirmed smooth image at the 15 FPS limit. Short same-camera samples showed
  WebKit CPU falling from 23.8% to 17.8% of one core; these are not a benchmark.

### Limitations

- HTTP(S) MJPEG and X11 only; no WebRTC, RTSP, HLS or Wayland support.
- Automatic stream pause on display power-off is not implemented.
- Thirty AI-assisted translations still need native-speaker review.
- See RELEASE_CHECKS.md and docs/VERIFICATION.cs.md for validation scope.

Live FPS selection and unlimited mode passed local transport and UI checks; target
validation of these new controls is pending.
