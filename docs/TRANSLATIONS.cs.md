# Jazykové soubory

[English](TRANSLATIONS.md) · [Česky](TRANSLATIONS.cs.md)

Jazykové soubory jsem zvolil jako jednoduché JSON, aby se daly upravovat běžným editorem a nový jazyk nevyžadoval změnu programu. Pro každý jazyk je samostatný soubor. Výběr jazyka se může řídit KlipperScreenem.

Jeden jazyk má jeden UTF-8 JSON soubor v `locales/`. Překlad nevyžaduje gettext ani kompilaci.
Texty lze upravit běžným editorem nebo přímo na GitHubu.

## Jazyky podle oficiálního KlipperScreenu

```text
ar bg cs da de de_formal en es et fa fr he hr hu it jp ko lt nl pl
pt pt_BR rs ru sk sl sv tr uk vi zh_CN zh_TW
```

Zdroj, datum a commit seznamu jsou v UPSTREAM_LOCALES.json. Přebírá se seznam
identifikátorů, nikoliv gettext soubory nebo oficiální schválení mých překladů.
KlipperScreenCam má vlastní texty. Dalších 30 překladů jsem připravil s pomocí AI a označil
`_meta.review_status = needs-native-review`. Čeština a angličtina byly součástí základu;
češtinu používám na své tiskárně.

Názvy souborů zachovávají upstream: například `de_formal.json`, `pt_BR.json`,
`jp.json`, `rs.json`, `zh_CN.json` a `zh_TW.json`.

## Jak přidat další jazyk

1. Zkopíruj `locales/en.json`, například na `locales/fi.json`.
2. V `_meta` změň `name` na název jazyka a `code` přesně na název souboru bez `.json`.
3. Překládej hodnoty vpravo; klíče vlevo neměň.
4. Pro pravolevé jazyky nastav `_meta.direction = rtl`, jinak ltr nebo údaj vynech.
5. Spusť `python3 launcher.py --check-locales`.
6. V KlipperScreenCam.conf nastav `language = fi` a restartuj službu KlipperScreenCam.

Příklad začátku souboru (finální soubor musí obsahovat všechny klíče z en.json):

```json
{
  "_meta": {
    "name": "Suomi",
    "code": "fi",
    "direction": "ltr",
    "translator": "Jméno překladatele",
    "review_status": "needs-native-review"
  },
  "window_title": "Tulostimen kamerat",
  "menu_title": "Kamerat"
}
```

JSON nemá komentáře a za poslední položkou nesmí být čárka. Vložené uvozovky zapisuj
jako `\"`. Kontrola hlásí chybějící/neznámé/duplicitní klíče, neplatný směr a nesoulad
kódu s názvem souboru. Chybějící text se za běhu doplní z angličtiny. Neplatný JSON
je potřeba opravit; program ponechá poslední úspěšně načtený vzhled.
Změny již zvoleného překladu se načítají automaticky bez restartu streamu.

Test přesné shody se snapshotem upstreamu je potřeba vědomě upravit, pokud přidáš jazyk,
který v upstreamu není. Produkční program nové JSON jazyky nijak neblokuje.

## Automatická volba a písma

`language = auto` přebírá volbu KlipperScreenu. Jeho `system_lang` přebírá jazyk OS.
Podporované příklady: `cs_CZ.UTF-8 → cs`, `pt-br → pt_BR`, `de-formal → de_formal`,
`ja_JP → jp`, `sr_RS → rs`, `zh-Hans → zh_CN`, `zh-Hant → zh_TW`.
Neznámý jazyk přejde do angličtiny.

Arabština, perština a hebrejština používají RTL menu. Poloha menu zůstává vpravo nahoře.
Směr názvu kamery se řídí obsahem; názvy pocházejí z Moonrakeru a nepřekládají se.

Pro všechna písma na minimálním OS může být potřeba:

```bash
sudo apt install --no-install-recommends fonts-noto-core fonts-noto-cjk
```

Instalátor přidává tato písma mezi závislosti. Při --no-deps je musí zajistit správce.
Skutečné RTL/CJK vykreslení ještě vyžaduje ověření na cílovém displeji.
