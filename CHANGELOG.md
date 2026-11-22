# Změny

## 0.2.0 — 2026-11-22

- Dokumentované skutečné nasazení samostatné verze na RPi5 / Debianu 13: obraz, ovládání a automatický start potvrzené uživatelem.
- Zachována oprava služby bez WorkingDirectory a validace systemd před instalací.
- Doplněny JSON překlady pro všech 32 variant podle zaznamenaného oficiálního seznamu KlipperScreenu.
- Nových 30 překladů označeno jako AI-assisted návrhy k jazykové revizi; nepřebíráme celé upstream gettext soubory.
- Opraven výběr regionálních variant pt_BR, zh_CN, zh_TW a de_formal; přidány ISO aliasy a system_lang.
- Pravolevé menu pro ar/fa/he a podpora písem Noto při instalaci.
- Anglický README, český README a návod pro druhý HDMI displej a oba dotyky krok za krokem.
- Doplněn postup aktualizace, návratu a vysvětlení výchozí kamery podle přesného názvu nebo UID.
- Přidány regresní testy jazyků/RTL a skutečné ověření systemd jednotky v Linux CI.

## 0.1.1 — 2026-11-22

- Oprava systemd služby: odstranění zbytečného WorkingDirectory, jehož uvozovky systemd považoval za součást cesty.
- Instalátor před instalací služby ověří jednotku pomocí systemd-analyze verify.
- Příčina chyby ověřena na RPi; uživatel následně potvrdil běh aplikace i automatický start.

## 0.1.0 — 2026-11-22

- Oddělení kamerového displeje do samostatného projektu KlipperScreenCam.
- Vlastní instalační a odinstalační postup a služba systemd.
- KlipperScreenCam.conf v adresáři konfigurace tiskárny.
- Pevná výchozí kamera, nastavení geometrie a pauza místního streamu.
- JSON překlady cs/en, fallback do angličtiny, validátor jazyků.
- Automatické přebírání jazyka, GTK barev a ikon motivu KlipperScreenu.
- Dotykové menu, stejně velké položky, dlouhé názvy, rolování a obnova streamu.
- Dokumentovaný přechod z původní instalace, návrat a pilotní ověření.

Historický stav 0.1.0: připraveno pro pilot. Následné nasazení a oprava jsou zaznamenány výše.
