# Changelog

[Česky](CHANGELOG.cs.md)

## 0.3.0 — 2026-11-22

### Camera display and controls

- Standalone X11 touch camera viewer for Klipper and Moonraker, with a separate
  service, installer and printer configuration file.
- Existing HTTP(S) MJPEG streams and camera names from Moonraker. Fixed startup
  camera by exact name or UID, independent of Mainsail.
- Full-window video, transparent overlays, theme SVG icons and GTK-computed colors
  from the local KlipperScreen installation; automatic theme and language changes.
- Scrollable camera menu, video off/on, measured source/forwarded FPS and live presets.
  Numeric presets 10/20/30 plus a sorted configured custom value have equal widths;
  Unlimited fills the remaining second-row space. Runtime changes are not persisted.
- Local frame limit defaults to 15 FPS, accepts 1–120 or `unlimited`, and drops
  compressed frames before WebKit without re-encoding. Upstream capture and remote
  viewers remain independent. Counters are averages rounded to whole numbers.
- Video off closes the actual local connection. Selecting a camera resumes it.
- Optional WebKit acceleration policy `off/auto/on`; default off. Hardware MJPEG
  decoding is not guaranteed.

### Sleep and shared wake

- Close the local stream after detecting X11 DPMS sleep, with configurable checks
  every 20 seconds by default. Keep the existing KlipperScreen blanking timeout.
- Optional `--shared-wake` integration dismisses KlipperScreen's black overlay and
  sends a nonblocking FIFO wake message for immediate camera resume.
- Preserve manual pause, selected camera and runtime FPS limit across sleep/wake.
- Sleep settings belong in `[display]`. Legacy `[stream]` entries remain accepted
  with a warning; duplicate definitions across sections are rejected.
- Guarded KlipperScreen source updates create timestamped backups. Both services
  must restart after installation. KlipperScreen updates may overwrite the patch.

### Installation and documentation

- Register the service in `moonraker.asvc` without duplicates, retaining existing
  entries and a backup. Moonraker restart remains manual.
- English primary documentation and Czech secondary guides, including step-by-step
  dual HDMI/touch setup, configuration, migration, sleep/wake and rollback.
- Editable JSON files for 32 locale variants, including all FPS labels and RTL support.
  Thirty AI-assisted translations remain open for native-speaker review.
- Automated configuration, transport, UI and platform checks; detailed evidence
  stays in RELEASE_CHECKS.md rather than the installation manual.

### Verification and limits

I verified the setup on my Raspberry Pi 5 with Debian 13, X11 and two 1024 × 600
HDMI touch displays, including startup after reboot, shared wake and immediate
camera resume. Later sleep/wake checks were completed on 2026-11-23 and are included
under this consolidated 0.3.0 release entry. Smooth 15 and 10 FPS video and actual
connection shutdown were checked on my printer; CPU observations are not benchmarks.

HTTP(S) MJPEG and X11 only; no WebRTC, HLS, RTSP or Wayland. The optional wake patch
supports the verified KlipperScreen source layout and refuses unknown layouts.
Other hardware, drivers, themes and language/font combinations need their own checks.
