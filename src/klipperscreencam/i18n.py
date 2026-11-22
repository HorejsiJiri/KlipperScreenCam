"""Editable UTF-8 JSON translations; English is the complete fallback."""
import json
import logging
import locale
import re
from pathlib import Path

LOG = logging.getLogger(__name__)


def read_language(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    data = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)
    if not isinstance(data, dict) or not isinstance(data.get("_meta"), dict):
        raise ValueError(f"{path.name}: expected an object with _meta")
    code = data["_meta"].get("code")
    name = data["_meta"].get("name")
    if code != path.stem or not isinstance(name, str) or not name.strip():
        raise ValueError(f"{path.name}: _meta.code must match filename; name is required")
    if not re.fullmatch(r"[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*", code):
        raise ValueError(f"{path.name}: invalid language code")
    if data["_meta"].get("direction", "ltr") not in ("ltr", "rtl"):
        raise ValueError(f"{path.name}: direction must be ltr or rtl")
    for key, value in data.items():
        if key != "_meta" and not isinstance(value, str):
            raise ValueError(f"{path.name}: {key} must be a string")
    return data


def canonical(code: str) -> str:
    return code.split(".", 1)[0].replace("_", "-").lower()


def html_language(code: str) -> str:
    return {"jp": "ja", "rs": "sr", "de_formal": "de"}.get(code, code.replace("_", "-"))


def load_language(directory: Path, requested: str) -> tuple[str, dict]:
    english = read_language(directory / "en.json")
    if requested in ("system_lang", "auto", ""):
        requested = locale.getlocale()[0] or "en"
    normalized = canonical(requested)
    aliases = {"ja": "jp", "sr": "rs", "zh": "zh-cn", "zh-hans": "zh-cn",
               "zh-hant": "zh-tw", "zh-hk": "zh-tw", "zh-sg": "zh-cn"}
    if normalized.startswith("zh-hant-"):
        normalized = "zh-tw"
    elif normalized.startswith("zh-hans-"):
        normalized = "zh-cn"
    available = {canonical(path.stem): path for path in directory.glob("*.json")}
    base = normalized.split("-", 1)[0]
    candidates = [normalized, aliases.get(normalized, normalized),
                  aliases.get(base, base), base, "en"]
    for code in dict.fromkeys(candidates):
        if not re.fullmatch(r"[a-z0-9-]+", code) or code not in available:
            continue
        path = available[code]
        translated = read_language(path)
        missing = set(english) - set(translated)
        if missing:
            LOG.warning("Translation %s is missing keys: %s", code, sorted(missing))
        return path.stem, {**english, **translated}
    return "en", english


def check_languages(directory: Path) -> list[str]:
    english = read_language(directory / "en.json")
    expected = set(english) - {"_meta"}
    problems = []
    seen = set()
    for path in sorted(directory.glob("*.json")):
        try:
            normalized = canonical(path.stem)
            if normalized in seen:
                problems.append(f"{path.name}: duplicate normalized language code")
            seen.add(normalized)
            data = read_language(path)
            keys = set(data) - {"_meta"}
            for kind, entries in (("missing", expected - keys), ("unknown", keys - expected)):
                if entries:
                    problems.append(f"{path.name}: {kind} keys {sorted(entries)}")
        except (OSError, ValueError) as error:
            problems.append(f"{path.name}: {error}")
    return problems
