# KlipperScreenCam

Samostatný dotykový kamerový displej pro tiskárny s Klipperem a Moonrakerem.
Na jednom monitoru zůstává KlipperScreen, na druhém běží KlipperScreenCam.
Přehrává existující HTTP MJPEG streamy; nemění nastavení kamer ani výběr ve webovém Mainsailu.

**Verze 0.3.0.**
Předchozí samostatnou verzi 0.2.3 uživatel nasadil a potvrdil funkční obraz, ovládání
a automatický start na RPi5 / Debianu 13 / X11 / dvou HDMI displejích 1024 × 600.
Výchozí limit je 15 FPS; uživatel potvrdil plynulý obraz. Nové překlady ještě potřebují kontrolu rodilými mluvčími.
Podrobné rozlišení ověřeného základu a nových změn je v [docs/VERIFICATION.cs.md](docs/VERIFICATION.cs.md).

[English README](README.md)

## Funkce

- Kamery a jejich názvy z Moonrakeru, ve stejném pořadí jako vrácený seznam.
- Jedna pevná výchozí kamera podle UID nebo názvu, nezávisle na Mainsailu.
- Video přes dostupnou plochu se zachováním poměru stran.
- Průhledné pozadí názvu a ikony nastavení přímo nad obrazem.
- Dotykové menu od horního pravého okraje, bez animace, se zavřením mimo nabídku nebo přes ×.
- Posuvník pro dlouhý seznam, stejná velikost položek podle nejdelšího názvu.
- Barvy vypočítané GTK ze skutečného motivu KlipperScreenu; SVG ikony z jeho instalace.
- Automatické převzetí změny motivu a jazyka (výchozí interval dvě sekundy).
- Jednoduše editovatelné JSON překlady: všech 32 variant z oficiálního seznamu KlipperScreenu, včetně RTL.
- Vypnutí/zapnutí pouze místního obrazu z menu. Při vypnutí se uzavře odběr streamu.
- Přeškrtnutá kamera a text „Obraz vypnut“ při pozastavení; výběr kamery obraz znovu zapne.
- U jedné kamery lze skrýt název; menu zůstává přístupné kvůli vypnutí obrazu.
- Nové spojení při výběru téže kamery a opakované pokusy po nahlášené chybě streamu.

## Instalace

**Potřebuješ nejdříve zprovoznit druhý displej?** Kompletní postup pro HDMI, rozšířenou plochu,
rozlišení, oba dotyky a trvalé spuštění je v [docs/SECOND_DISPLAY.cs.md](docs/SECOND_DISPLAY.cs.md).

Podporovaný základ: Linux s apt/systemd, X11, GTK 3, WebKitGTK 4.1 a samostatně
fungující KlipperScreen. Výchozí konfigurace očekává druhý monitor na souřadnicích
`1024,0` a rozměr `1024 × 600`. Aplikace sama nemění HDMI režimy ani mapování dotyků.

Po zkopírování nebo naklonování projektu například do `~/KlipperScreenCam`:

```bash
cd ~/KlipperScreenCam
bash scripts/install.sh
nano ~/printer_data/config/KlipperScreenCam.conf
python3 launcher.py --check
python3 launcher.py --list-cameras
```

Instalátor vytvoří službu, ale standardně ji **nespustí a nepovolí při startu**.
Po kontrole konfigurace a případném odstranění starého automatického spouštění:

```bash
sudo systemctl enable --now KlipperScreenCam
```

Pro novou instalaci bez starého náhledu lze použít `bash scripts/install.sh --enable`.
Nepouštěj celý instalátor přes sudo; administrátorská oprávnění si vyžádá jen pro apt a službu.
Existující `KlipperScreenCam.conf` při opakované instalaci nepřepíše.

**Přechod ze staré verze:** nejprve přečti [docs/MIGRATION.cs.md](docs/MIGRATION.cs.md).
Nespouštěj současně starý náhled z `start-displays.sh` a novou službu.
Pro první nasazení dodaného archivu je připravený [docs/DEPLOY.cs.md](docs/DEPLOY.cs.md).

## Restart přes Moonraker

Instalátor doplní `KlipperScreenCam` do `~/printer_data/moonraker.asvc` bez duplicit
a zachová ostatní služby. Potom ve vhodnou dobu restartuj Moonraker. Přesný postup včetně API: [návod](docs/MOONRAKER.cs.md).

## Konfigurace

Hlavní soubor je `~/printer_data/config/KlipperScreenCam.conf`, dostupný v editoru
konfigurací Mainsailu. Vzor je v [config/KlipperScreenCam.conf](config/KlipperScreenCam.conf).

```ini
[main]
default_camera = UID_Z_VYPISU_MOONRAKERU
language = auto
theme = auto
```

UID je stabilní i po přejmenování kamery. Zjistíš ho přes `python3 launcher.py --list-cameras`.
Lze použít i přesný název, například `default_camera = Tryska`.
Prázdná hodnota znamená první povolenou kameru. Chybějící nebo zakázaná výchozí kamera
vede k první dostupné kameře a upozornění v logu. Běžné přepínání výchozí kameru nemění.

```ini
[display]
x = 1024
y = 0
width = 1024
height = 600
hide_name_single_camera = true

[stream]
max_fps = 15
start_paused = false
```

`start_paused = true` spustí rozhraní bez odběru obrazu; zapneš jej z menu.
Pozastavení během provozu platí do dalšího spuštění, nepřepisuje konfiguraci.
Vypnutí místního obrazu snižuje práci našeho vykreslovače a počet odběratelů;
Crowsnest a ostatní diváci dále běží, proto nemusí klesnout veškerá zátěž kamerové služby.

Po změně hlavní konfigurace nebo seznamu kamer:

```bash
sudo systemctl restart KlipperScreenCam
```

Motiv, jazyk a texty překladů se průběžně načítají automaticky.
Podrobnosti o jazycích: [docs/TRANSLATIONS.cs.md](docs/TRANSLATIONS.cs.md).

## Zhasínání displejů

KlipperScreenCam nemá vlastní časovač zhasínání, nezakazuje DPMS ani nespouští
`xset s off` / `xset -dpms`. Ponechává správu displejů KlipperScreenu a X serveru.
Pokud KlipperScreen používá globální X11 DPMS, jeho nastavení se může vztahovat na oba výstupy.
Softwarový spořič v samotném okně KlipperScreenu automaticky nezakryje náš displej.
Skutečné chování je nutné ověřit na cílové konfiguraci.

**Zhasnutí přes DPMS není totéž jako zastavení streamu.** Pro snížení zátěže slouží
volba Vypnout obraz. Automatické pozastavování podle DPMS v této verzi není implementované.

## Omezení

- Podporovány jsou HTTP(S) MJPEG streamy. WebRTC, HLS, RTSP a přímé otevření `/dev/video*` nejsou cílem této verze.
- Na jedné X11 ploše musí být předem správně nastavené oba displeje a dotyky.
- Nespravuje displeje přes Wayland a nepřidává správce oken.
- Při nahlášené chybě se stream opakuje s prodlevou až do konfigurovaného maxima.
  Tiché zastavení snímků na stále otevřeném HTTP spojení nemusí prohlížeč oznámit.
  Klepnutí na stejnou kameru v menu vždy vynutí nové spojení.
- Více odběratelů znamená další dekódování a přenos. Souběh KlipperScreen/Mainsail/náš displej patří do pilotu.
- Převzetí vzhledu používá skutečné barvy a ikony motivu, ne veškeré rozměry a CSS KlipperScreenu.
- Konfigurace KlipperScreenu s uloženým blokem `#~#` a běžnými `[include ...]` je podporovaná.

## Diagnostika a odinstalace

```bash
systemctl status KlipperScreenCam --no-pager
journalctl -u KlipperScreenCam -n 100 --no-pager
python3 launcher.py --check-locales
python3 -m unittest discover -s tests -v
bash scripts/uninstall.sh
```

Odinstalace odstraní jen naši službu. Konfigurace, překlady i zdrojové soubory zůstanou.
Nezasahuje do KlipperScreenu, Moonrakeru ani Crowsnestu.

## Projekt a stav ověření

```text
KlipperScreenCam/
├── launcher.py
├── config/KlipperScreenCam.conf
├── locales/                    # jeden editovatelný JSON pro každý jazyk
├── src/klipperscreencam/        # konfigurace, Moonraker, GTK, překlady, GUI
├── web/index.html              # dotykové rozhraní a přehrávání MJPEG
├── assets/                     # vlastní náhradní ikony
├── scripts/                    # instalace / odinstalace samostatné služby
├── tests/
└── docs/
```

Instalace je podporovaná přímo ze zdrojového adresáře; `pip install` není instalační postup aplikace.
Zdrojové soubory tohoto projektu byly sestaveny podle ověřeného chování z předchozího řešení.
Verze 0.2.3 byla nasazena na RPi; obraz s limitem 15 FPS je podle uživatele plynulý.
Rozsah kontrol a další scénáře: [docs/TESTING.cs.md](docs/TESTING.cs.md).

Projekt není oficiální součástí KlipperScreenu. Ikony z jeho motivů se čtou z místní instalace,
nejsou do repozitáře kopírované. Licence tohoto nového projektu zatím nebyla zvolena;
před veřejným zveřejněním doplň LICENSE a údaje autora. Tento balíček není automaticky publikovaný na GitHub.

## Skutečné vypnutí obrazu

Spojení s kamerou nově vlastní Python. Při vypnutí uzavře skutečný TCP přenos
a potvrdí zastavení do rozhraní. WebKit načítá jen jednorázový lokální přenos; stará adresa
po vypnutí nemůže spustit kameru znovu. Nejde jen o skrytí obrazu nebo odstranění img.src.
Přepnutí kamery uzavře předchozí spojení. Ostatní diváci a Crowsnest nejsou vypínáni.
Uzavření přenosu bylo ověřeno automatickými testy i přímo na RPi.

## Volitelná GPU akcelerace

V sekci `[display]` nastavit `hardware_acceleration = on`, `auto` nebo `off`.
Při chybějící volbě zůstává off. Jde o vykreslování WebKitu, nikoliv záruku hardwarového
dekódování MJPEG. [Postup porovnání a návratu](docs/ACCELERATION.cs.md).

## Omezení místních FPS

V sekci `[stream]` lze nastavit `max_fps = 15` (výchozí 15). Omezuje pouze místní
vykreslování, původní stream se dál čte. Podrobnosti: [FPS](docs/FPS.cs.md).

Menu nabízí 10, 20, 30 FPS a Neomezeně. Změna platí ihned bez nového spojení
a nezapne vypnutý obraz. Po restartu služby se obnoví max_fps z konfigurace.
V konfiguraci lze použít také `max_fps = unlimited`. Vlastní číselná hodnota se
vloží mezi tlačítka ve vzestupném pořadí bez duplicit. První řádek má tři tlačítka,
číselná tlačítka mají stejnou šířku a Neomezeně vyplní zbytek druhého řádku.
Pořadí menu: kamery, červené vypnutí/zapnutí obrazu s ikonou, nadpis Limity snímků,
naměřené FPS a tlačítka limitů.
Postup nasazení a ověření: [TEST_0.3.0.cs.md](docs/TEST_0.3.0.cs.md).
