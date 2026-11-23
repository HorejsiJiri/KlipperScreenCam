#!/usr/bin/env python3
"""Build source ZIP/TAR.GZ archives and checksums without runtime/private files."""
import argparse
import hashlib
from pathlib import Path
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from klipperscreencam import __version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    folders = {".github", "assets", "config", "docs", "locales", "scripts", "src", "tests", "web"}
    names = {".gitattributes", ".gitignore", "launcher.py", "pyproject.toml"}
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in (".git", "__pycache__", "node_modules", "work") for part in relative.parts):
            continue
        if path.suffix in (".pyc", ".pyo", ".log") or ".bak" in path.name:
            continue
        if len(relative.parts) == 1:
            if path.name not in names and path.suffix != ".md" and path.name not in ("LICENSE", "NOTICE"):
                continue
        elif relative.parts[0] not in folders:
            continue
        if path.is_symlink():
            raise ValueError(f"Refusing to package a symlink: {relative}")
        files.append(path)
    prefix = f"KlipperScreenCam-{__version__}"
    archives = [output / (prefix + ".zip"), output / (prefix + ".tar.gz")]
    with zipfile.ZipFile(archives[0], "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, "KlipperScreenCam/" + path.relative_to(ROOT).as_posix())
    with tarfile.open(archives[1], "w:gz", compresslevel=9) as archive:
        for path in files:
            info = archive.gettarinfo(str(path), "KlipperScreenCam/" + path.relative_to(ROOT).as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if path.suffix == ".sh" or path.name in ("launcher.py", "service.py", "package.py") else 0o644
            with path.open("rb") as stream:
                archive.addfile(info, stream)
    with zipfile.ZipFile(archives[0]) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
    with tarfile.open(archives[1]) as archive:
        assert len(archive.getmembers()) == len(files)
    checksums = "".join(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n"
                        for path in archives)
    (output / (prefix + "-SHA256SUMS.txt")).write_text(checksums, encoding="ascii")
    print(f"Packaged {len(files)} source files; no Git metadata or runtime caches.")
    for path in archives:
        print(path)


if __name__ == "__main__":
    main()
