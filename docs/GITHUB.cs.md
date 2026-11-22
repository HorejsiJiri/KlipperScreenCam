# Příprava pro GitHub

Balíček obsahuje anglický README, český README, konfiguraci, návody, jazykové soubory,
testy a workflow GitHub Actions. Zdrojový adresář má vlastní lokální Git repozitář;
archivy záměrně neobsahují jeho interní metadata ani lokální cache.

Projekt je samostatný a není oficiální komponentou KlipperScreenu. Názvy jazyků vycházejí
z veřejného snapshotu; naše nové překlady jsou samostatné návrhy k revizi. Licence projektu
zatím nebyla vlastníkem vybraná — tato příprava ji automaticky nepřiřazuje.

Před nahráním zkontroluj, že nepřidáváš skutečnou konfiguraci tiskárny, logy, hesla nebo
soukromé snímky kamer. V `config/` patří vzorová konfigurace; živý soubor zůstává v printer_data.

Pokud pracuješ s rozbaleným archivem bez .git, vytvoř repozitář:

```bash
git init -b main
```

Po kontrole souborů můžeš připravit první commit:

```bash
git add .
git commit -m "Release KlipperScreenCam 0.2.0"
```

Na GitHubu založ prázdný repozitář KlipperScreenCam. V následujícím příkladu nahraď
TVUJ_UCET vlastním účtem nebo organizací:

```bash
git remote add origin https://github.com/TVUJ_UCET/KlipperScreenCam.git
git push -u origin main
```

Pokud origin už existuje, nejdříve ověř jeho URL pomocí `git remote -v`; nevytvářej druhý
origin a neměň jej naslepo. GitHub Actions pak spustí kontroly. Jejich výsledek zkontroluj
před označením releasu a přiložením archivů. V této přípravě žádný push ani publikace neproběhly.
