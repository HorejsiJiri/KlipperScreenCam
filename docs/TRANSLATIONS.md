# Language files

[English](TRANSLATIONS.md) · [Česky](TRANSLATIONS.cs.md)

I use one editable UTF-8 JSON file per language in `locales/`. No gettext tools or
compilation are needed. `language = auto` follows KlipperScreen; an explicit locale
filename without `.json` selects a fixed language.

The recorded upstream snapshot contains these 32 identifiers:

```text
ar bg cs da de de_formal en es et fa fr he hr hu it jp ko lt nl pl
pt pt_BR rs ru sk sl sv tr uk vi zh_CN zh_TW
```

The upstream source and commit are in [UPSTREAM_LOCALES.json](UPSTREAM_LOCALES.json).
I copied the identifier list, not upstream translation files. The 30 additional
AI-assisted translations are marked `needs-native-review`; Czech and English form
the original baseline. These translations are not endorsed by KlipperScreen.

## Add or edit a language

1. Copy `locales/en.json`, for example to `locales/fi.json`.
2. Set `_meta.code` to the filename without `.json` and `_meta.name` to its display name.
3. Translate values, keeping every key and placeholder unchanged.
4. Use `_meta.direction = rtl` for right-to-left text; otherwise use `ltr`.
5. Validate, then select the language in `[main]` and restart the service.

```bash
python3 launcher.py --check-locales
```

JSON has no comments or trailing commas. Escape embedded quotes. Validation catches
unknown, missing and duplicate keys and invalid metadata. Missing runtime strings
fall back to English. Edits to the selected translation are detected automatically
without restarting the stream; invalid JSON must be fixed, and the last valid
appearance remains in use. Keep all FPS menu labels translated as well.

Locale aliases include regional and legacy names. Noto core/CJK fonts are installed
for minimal systems. Native review and real-screen checks remain welcome, especially
for RTL and CJK layouts. If adding a language absent from the upstream snapshot,
update the explicit snapshot test intentionally; the application accepts new JSON locales.
