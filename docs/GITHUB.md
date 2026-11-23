# Prepare and publish on GitHub

[English](GITHUB.md) · [Česky](GITHUB.cs.md)

English is the primary project documentation; Czech is the secondary version.
`README.md` links to the English guides, while `README.cs.md` links to Czech guides.
Each current guide links to its counterpart. Keep behavior, commands and defaults
consistent when changing either language.

## Files to upload

The source ZIP contains the project directory, including `.github` workflows,
configuration example, editable locales, source, tests and documentation. Extract
it first and upload the contents of `KlipperScreenCam/` to the repository root.
Uploading only the ZIP does not replace the source tree. Include hidden `.github`
and `.gitignore` files; exclude local environments, runtime configuration and caches.

Use Git, GitHub Desktop or GitHub's upload interface to commit the prepared files.
Review the diff before committing. Keep private printer settings out of the repository.

## Release assets

```bash
python3 scripts/package.py --output dist
```

This produces source ZIP, TAR.GZ and SHA256 checksums. The existing public release
is v0.3.0; the sleep/wake additions and bilingual documentation are included in this revision.
The changelog consolidates them under 0.3.0 dated 2026-11-22 as chosen for this project.
Changing an existing release's assets and source tag is an explicit publication step,
not an effect of building a local package.

The release workflow is manual. Review `.github/workflows/release.yml` before use:
it checks the selected commit and refuses an existing release rather than silently
replacing it. Use the appropriate manual asset/tag procedure if intentionally
replacing v0.3.0. Check Actions after source changes.

Suggested description: “A touch camera display for Klipper and Moonraker, styled to
match KlipperScreen, with camera switching, local FPS controls and display sleep support.”
Suggested topics: klipper, klipperscreen, moonraker, mainsail, raspberry-pi, camera, touchscreen.

The one-time `refresh-0.3.0.yml` workflow updates the existing release after successful
Checks. It accepts only the known original tag or its own commit, refusing other tag
changes. Ordinary source pushes do not trigger this refresh.
