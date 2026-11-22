# Stav ověření — 0.2.0

Datum: 2026-11-22. Rozlišujeme skutečné výsledky nasazení od místních testů.

## Potvrzeno uživatelem na cílovém RPi

Prostředí: Raspberry Pi 5 Model B Rev 1.0, Debian GNU/Linux 13.8 (Trixie),
KlipperScreen přes X11 a dva HDMI dotykové displeje 1024 × 600.

- Původní rozložení 2048 × 600 a mapování dotyků bylo zachováno při migraci.
- Aplikace byla převedena ze společného skriptu na samostatnou systemd službu.
- Instalátor 0.1.0 vytvořil neplatný WorkingDirectory s uvozovkami. Systemd jej odmítl.
  Řádek byl odstraněn; aplikace jej nepotřebuje.
- Po opravě služba hlásila active. Log potvrdil motiv z-bolt, češtinu a kameru z Moonrakeru.
- Uživatel výslovně potvrdil funkční obraz a ovládání nového náhledu.
- Uživatel potvrdil automatický start. Samostatný záznam bootu nebyl dodán.

0.1.1 obsahuje opravu generátoru služby. 0.2.0 na ni navazuje doplněním jazyků a dokumentace.
Běžící instalaci RPi tento krok neaktualizoval na 0.2.0.

## Místní automatické kontroly 0.2.0

- Testy konfigurace, překladů, výchozí kamery, nastavení KlipperScreenu a generování služby.
- Shoda s 32 jazyky oficiálního upstreamu ve zdokumentovaném commitu.
- Výběr všech jazyků, regionálních variant a aliasů, RTL/LTR a fallback do angličtiny.
- JSON validace, shoda klíčů a kontrola duplicit; syntaxe Pythonu, Bash a JavaScriptu.
- Testy rozhraní v headless prohlížeči: menu, výběr, nové spojení téže kamery,
  pauza, zapnutí výběrem, jedna kamera, dlouhé názvy, rolování, změna barev bez restartu
  streamu, skrytí kurzoru, bezpečné vykreslení názvů a přepnutí jazyka/RTL.

Aktuální výsledky jsou v RELEASE_CHECKS.md. Linuxový CI test ověřuje generovanou jednotku
přes skutečné systemd-analyze verify; na Windows se tato specifická kontrola přeskakuje.

## Co není potvrzené

- Nových 30 překladů nebylo posouzeno rodilými mluvčími; jsou označené jako návrhy.
- Úplná verze 0.2.0 a její RTL/CJK vykreslení ještě nebyly nasazeny na RPi.
- Pokles CPU a ukončení síťového odběru při pauze nebyly externě změřeny.
- Úplný souběh všech diváků a všechny druhy výpadků nemají kompletní testovací protokol.
- Zhasnutí/probuzení obou výstupů podle DPMS ani všechny motivy nebyly potvrzené.

Pilotní seznam je v TESTING.cs.md. Browser test nenahrazuje GTK/WebKitGTK test na RPi.
