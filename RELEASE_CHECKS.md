# Release checks — 0.2.0

Date: 2026-11-22.

## Local results

- Python unittest suite: 27 tests run; 26 passed, 1 skipped (real Linux/systemd verification).
- JSON validation: all 32 locale files valid and complete, matching the recorded upstream locale set.
- Locale selection tests: all 32 identifiers, regional forms, aliases, OS language and RTL metadata passed.
- Example configuration validation and Python compilation passed.
- Installer/uninstaller Bash syntax checks passed.
- Browser UI checks passed in headless Microsoft Edge (Chromium) through Playwright.
  Includes selection/reconnect, pause/resume, resume by camera selection, one camera,
  scrolling/long labels, CSS theme change without stream reload, hidden cursor,
  safe text names, all locale switches and RTL menu alignment.

The workflow in .github/workflows/checks.yml also runs the native systemd validation on Linux.
This release has not been pushed, and no GitHub Actions run is claimed here.

## Target deployment evidence

The user confirmed the standalone 0.1.x viewer's picture, controls and automatic start
on RPi5 / Debian 13 / X11 / two 1024 × 600 HDMI touch displays after removing the invalid
quoted WorkingDirectory. This fix remains in 0.2.0.

The new 0.2.0 locale/RTL/font changes have not been installed on that RPi in this step.
New translations are AI-assisted drafts, not native-reviewed or official upstream translations.
See docs/VERIFICATION.cs.md and docs/TESTING.cs.md for exact limits and remaining checks.

## Source packages

Build the ZIP/TAR.GZ and SHA-256 checksums with:

```bash
python3 scripts/package.py
```

Packages exclude Git metadata, local caches, node_modules and work files. They do not
include the live printer configuration, logs or private camera images.
