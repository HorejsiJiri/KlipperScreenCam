# Ověření

[English](TESTING.md) · [Česky](TESTING.cs.md)

Při vývoji kombinuji automatické kontroly s praktickými zkouškami na tiskárně. Níže je postup, který používám pro ověření změn. Seznam scénářů není tvrzením, že jsem všechny z nich dokončil; konkrétní výsledky zaznamenávám do VERIFICATION.cs.md.

## Lokální kontroly bez RPi

```bash
python3 -m unittest discover -s tests -v
python3 launcher.py --check-locales
python3 launcher.py --config config/KlipperScreenCam.conf --check
python3 -m compileall -q launcher.py src scripts
bash -n scripts/install.sh scripts/uninstall.sh
```

`tests/test_ui.cjs` testuje rozhraní v headless Chromium přes Playwright, například výběr
kamery, skrytí názvu při jediné kameře, dlouhý seznam, překlady a vypnutí místního streamu.
Playwright je jen vývojový nástroj, na RPi jej aplikace nepotřebuje.

```bash
npm install --no-save --package-lock=false playwright
npx playwright install chromium
node tests/test_ui.cjs
```

Tyto kontroly nejsou důkazem správného chování GTK/WebKitGTK na RPi.

## Pilot na RPi

1. Ověřit dvě oddělené plochy a dotyky. Na HDMI-1 KlipperScreen, na HDMI-2 okno KlipperScreenCam.
2. Výchozí kamera podle UID; jiný výběr během provozu; restart na pevnou výchozí kameru.
3. Souběžný obraz v Mainsailu, KlipperScreenu a KlipperScreenCam.
4. Otevření/zavření kamery v KlipperScreenu; druhý displej se nesmí trvale zaseknout.
5. Stejná kamera z menu musí vynutit nové spojení.
6. Vypnout obraz a ověřit, že místní HTTP odběr skončil, jiní diváci dále fungují.
7. Jediná kamera: název skrytý, kolečko a vypnutí/zapnutí stále dostupné.
8. Více kamer a dlouhé názvy: dotykové posouvání, viditelný posuvník, stejné výšky položek.
9. Motivy z-bolt, colorized a další instalované motivy: pozadí, text, aktivní položka a ikony.
10. Čeština, angličtina a nový JSON jazyk; změna motivu/jazyka nesmí restartovat stream.
11. Zhasnutí a probuzení přes skutečné nastavení KlipperScreenu/DPMS.
12. Úplný restart RPi; start nové služby a zachování HDMI/dotykového rozložení.
13. Sledovat CPU, paměť a teplotu při jedné kameře, při souběhu a při vypnutí místního obrazu.

Do protokolu zaznamenat verzi projektu, OS, model RPi, verze GTK/WebKit, motiv,
kamerovou službu a výsledek každého bodu. Aktuální potvrzené výsledky jsou ve VERIFICATION.cs.md; zbytek seznamu je plán dalších kontrol.
