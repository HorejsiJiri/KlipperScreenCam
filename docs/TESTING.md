# Validation checklist

[English](TESTING.md) · [Česky](TESTING.cs.md)

I keep routine test output separate from the installation guide. Automated checks
support development; they do not replace validation on the printer's actual X11,
GTK/WebKit, touch and camera setup.

```bash
python3 -m unittest discover -s tests -v
python3 launcher.py --check-locales
python3 launcher.py --config config/KlipperScreenCam.conf --check
```

Browser checks use Playwright through `tests/test_ui.cjs`; configure
`KSC_PLAYWRIGHT_MODULE` and `KSC_BROWSER_PATH` for the local installation if needed.
Linux checks cover systemd and actual FIFO behavior; some are skipped on Windows.

On the printer, check both display positions and touch mappings, camera switching,
reselecting the same camera, manual video off/on, long names and scrollable lists,
live FPS presets, configuration defaults after restart, theme/language changes,
recovery from reported camera errors, and simultaneous Mainsail access.
For sleep integration follow [sleep/wake verification](RPI_SLEEP.md), including both
touchscreens, actual local transport closure, manual pause and a complete reboot.
See [verification notes](VERIFICATION.md) and [release checks](../RELEASE_CHECKS.md).
