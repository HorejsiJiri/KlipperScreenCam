# Contributing

KlipperScreenCam is independent, not an official KlipperScreen component.
Include the observed environment and validation results with bug reports or changes.

## Translations

Edit a UTF-8 JSON file in `locales/`; no code changes or compilation are required.
Copy en.json for a new language and keep all message keys unchanged. `_meta.code`
must match the filename without .json. Use `_meta.direction = "rtl"` for right-to-left text.
Select a language with `[main] language` in KlipperScreenCam.conf.

Locale identifiers match the upstream snapshot in docs/UPSTREAM_LOCALES.json.
The 30 newly prepared translations are AI-assisted drafts, not official translations.
Native-speaker corrections are welcome. Do not mark a draft as reviewed without review.

```bash
python3 launcher.py --check-locales
python3 -m unittest discover -s tests -v
```

The exact-upstream-set test needs an intentional update if you add a language outside
that snapshot. The application discovers JSON files without a hardcoded registry.

## Development

```bash
python3 -m compileall -q launcher.py src scripts
bash -n scripts/install.sh scripts/uninstall.sh
npm install --no-save --package-lock=false playwright
npx playwright install chromium
node tests/test_ui.cjs
```

GTK/WebKitGTK and systemd need additional Linux/RPi validation. Browser tests do not prove
a successful RPi installation. Do not bundle private configuration, credential-bearing
camera URLs, logs or camera images.

The project owner's license choice is pending; this document does not assign a license.
