# Release checks — 0.3.0 (test candidate)

Date: 2026-11-22. First public release baseline, with a default local limit of 15 FPS.

## Local checks completed

- Python unittest: 48 tests run, 47 passed, 1 skipped (native Linux/systemd verification).
- All 32 JSON locales and the example configuration validated.
- Headless Edge/Playwright UI checks passed: selection, reconnect, pause/resume,
  same-camera resume, one camera, scrolling, long labels, theme changes, hidden cursor,
  escaped names, all locales and RTL.
- Real continuous multipart MJPEG tests cover upstream closure, stale URLs, camera
  switching, local frame limiting, original JPEG bytes, fragmented multipart data,
  streams without Content-Length and an independent second client.
- The Linux GitHub Actions workflow additionally runs native systemd validation.

These are local results for the final source package. Earlier baseline Actions runs
passed, but this package has not yet been uploaded or checked in GitHub Actions.

## Target deployment

The user confirmed picture, touch controls and automatic startup on Raspberry Pi 5,
Debian 13, X11 and two 1024 × 600 HDMI touch displays. Actual stream shutdown was
confirmed using logs and sockets, with a short total CPU sample falling to about 2%.
Version 0.2.3 was deployed with max_fps = 15 and the user confirmed smooth video.
Same-camera short samples showed WebKit at 23.8% versus 17.8% of one core;
these do not constitute a controlled benchmark.

WebKit acceleration policy on was requested successfully; actual GPU decoding is
not established. All new translations, themes and failure scenarios have not been
exhaustively tested. Moonraker service control instructions are based on upstream
documentation and have not yet been user-verified on the target.

See docs/VERIFICATION.cs.md and docs/TESTING.cs.md for scope and remaining checks.

## Packaging

```bash
python3 scripts/package.py
```

ZIP/TAR.GZ archives and SHA-256 checksums exclude Git metadata, caches and runtime
files. They contain sample configuration and a synthetic test JPEG, not live printer
configuration, logs or private camera images. The existing Moonraker service allowlist
is preserved; the installer appends its service once and keeps a first-change backup.
Four installer tests cover preservation, idempotence, file creation, missing directories
and retention of an existing backup.

## New controls awaiting target testing

Live 10/20/30/unlimited selection, changes while paused, unchanged stream URL,
all translated FPS labels and case-insensitive unlimited configuration passed locally.
A real source test switches a running limited connection to unlimited without
opening a second camera connection. Default configuration remains 15 FPS.

## FPS diagnostics

All live presets were tested against a real source faster than 30 FPS. Actual
forwarded counters changed with each limit on one connection, and unlimited
matched source frame rate. UI checks cover both rate labels in all 32 languages.
On the target, logs confirm menu choices reach the host, but actual FPS effect
still needs the new counters. No production root cause is asserted.

## Revised menu 0.3.0

UI checks verify section order, custom 15/20/120/unlimited configuration, numeric
button widths, three buttons in the first row, remaining-space alignment, red
video toggle and slash visibility when paused/resumed. Local screenshot inspected.
Target GTK/WebKit validation of this layout remains pending.
