# Jak udržuji projekt a vydávám balíčky

[English](GITHUB.md) · [Česky](GITHUB.cs.md)

Projekt zveřejňuji v repozitáři [HorejsiJiri/KlipperScreenCam](https://github.com/HorejsiJiri/KlipperScreenCam).
Verze 0.3.0 už má vlastní [vydání](https://github.com/HorejsiJiri/KlipperScreenCam/releases/tag/v0.3.0)
s instalačními archivy a kontrolními součty. Následující postup si ponechávám pro další změny.

## Běžná práce se zdroji

Pracuji v klonu existujícího repozitáře. Nevytvářím kvůli každému vydání nový
repozitář a nepřepisuji jeho historii. Před odesláním zkontroluji změny:

```bash
git status
git diff
git remote -v
```

Do repozitáře patří vzorová konfigurace, zdroje, dokumentace, překlady a testy.
Živou konfiguraci tiskárny, hesla, logy a soukromé obrazy kamer do něj nepřidávám.

```bash
git add .
git commit -m "Update KlipperScreenCam documentation"
git push origin main
```

Použij zprávu odpovídající své změně. Pokud přispíváš z vlastního účtu, připrav
větev nebo fork a pull request místo přímého zápisu do mé větve main.

## Vydání

Pro publikování používám ručně spouštěný postup **Publish release** v GitHub Actions.
Verzi čte z projektu, sestaví ZIP a TAR.GZ, přidá SHA-256 a před zveřejněním ověří
úspěšný výsledek běžných kontrol pro stejný commit. Existující vydání nepřepisuje.

1. U nové verze uprav číslo v pyproject.toml i src/klipperscreencam/__init__.py.
2. Doplň changelog a odpovídající dokumentaci.
3. Odešli změny a počkej na zelené Checks.
4. V Actions otevři Publish release a spusť Run workflow pro main.
5. Zkontroluj dokončení a přílohy nového vydání.

Samotné lokální zabalení nic nepublikuje:

```bash
python3 scripts/package.py
```

## Changelog a překlady

Přípravné iterace jsem shrnul do prvního vydání 0.3.0. Další veřejná vydání budou
mít vlastní sekci s verzí a datem; starší záznamy ponechávám. Překlady mají vlastní
JSON soubory. Připomínky rodilých mluvčích uvítám.

KlipperScreenCam není oficiální komponenta KlipperScreenu. Licenci projektu jsem
zatím nezvolil.
