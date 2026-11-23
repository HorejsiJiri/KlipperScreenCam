# KlipperScreenCam

**Verze 0.3.0** · [English](README.md)

KlipperScreenCam jsem vytvořil pro svou tiskárnu, protože jsem chtěl mít ovládání
KlipperScreenu na jednom displeji a přehledný obraz z kamer na druhém. Kamery dál
používám i vzdáleně v Mainsailu. Z displeje mohu přepínat kamery, omezit snímkovou
frekvenci nebo místní obraz úplně vypnout.

Aplikaci používám s Raspberry Pi 5, Debianem 13, X11 a dvěma HDMI dotykovými
displeji 1024 × 600. Z tohoto zapojení vycházejí příklady v návodech.

[Úplná konfigurace](docs/CONFIGURATION.cs.md) · [Přehled změn](CHANGELOG.cs.md)

## Co aplikace umí

- Načítá kamery a jejich názvy z Moonrakeru a používá existující HTTP(S) MJPEG streamy.
- Má pevnou výchozí kameru podle názvu nebo UID, nezávislou na výběru v Mainsailu.
- Zobrazuje video přes plochu druhého displeje se zachováním poměru stran.
- Přebírá barvy, ikony a jazyk z místní instalace KlipperScreenu.
- Nabízí dotykové menu s posouváním dlouhého seznamu kamer.
- Umí skutečně zastavit místní přenos obrazu, aniž vypne kameru ostatním divákům.
- Umožňuje měnit limit FPS za běhu a ukazuje FPS ze zdroje i předávané WebKitu.
- Obsahuje 32 samostatných, snadno upravitelných jazykových JSON souborů.
- Běží jako samostatná služba s vlastním instalačním a odinstalačním skriptem.

KlipperScreenCam je můj samostatný projekt, nikoli oficiální součást KlipperScreenu.
Ikony jeho motivů čtu z místní instalace; do projektu je nekopíruji.

## Instalace

Potřebuješ funkční KlipperScreen, Moonraker, kamery a Linux s apt/systemd, X11,
GTK 3 a WebKitGTK 4.1. Aplikaci spouštěj přímo ze zdrojového adresáře.

**Pokud ještě nemáš připravené dva displeje a oba dotyky, začni
[návodem pro druhý displej](docs/SECOND_DISPLAY.cs.md).**

Stáhni [vydání 0.3.0](https://github.com/HorejsiJiri/KlipperScreenCam/releases/tag/v0.3.0),
rozbal projekt do `~/KlipperScreenCam` a pod běžným účtem tiskárny spusť:

```bash
cd ~/KlipperScreenCam
bash scripts/install.sh
nano ~/printer_data/config/KlipperScreenCam.conf
python3 launcher.py --check
python3 launcher.py --list-cameras
```

Instalátor doplní závislosti, vytvoří službu a ponechá existující konfiguraci.
Ve výchozím režimu službu ještě nespustí. Po kontrole konfigurace:

```bash
sudo systemctl start KlipperScreenCam
systemctl status KlipperScreenCam --no-pager
```

Jakmile ověříš obraz a dotyk, povol automatické spouštění:

```bash
sudo systemctl enable KlipperScreenCam
```

Celý postup včetně správy přes Moonraker je v [instalačním návodu](docs/DEPLOY.cs.md).
Pokud přecházíš ze starého náhledu ve společném spouštěcím skriptu, použij
[návod k přechodu](docs/MIGRATION.cs.md). [Aktualizace](docs/UPDATE.cs.md) má vlastní postup.

## Konfigurace

Nastavení mám v `~/printer_data/config/KlipperScreenCam.conf`, kde ho mohu upravovat
i z Mainsailu. Úplný vzor je v [config/KlipperScreenCam.conf](config/KlipperScreenCam.conf).
Následující ukázku použij jako orientaci; nevytvářej duplicitní sekce.

```ini
[main]
default_camera = Cam2
language = auto
theme = auto

[display]
display = :0
xauthority = ~/.Xauthority
x = 1024
y = 0
width = 1024
height = 600
hardware_acceleration = off
hide_name_single_camera = true

[stream]
max_fps = 15
start_paused = false
```

Výchozí kamera může být zadaná přesným názvem z Moonrakeru nebo UID. UID se nemění
při přejmenování kamery. Obojí vypíše `python3 launcher.py --list-cameras`.
Cesta zařízení z Crowsnestu, například `/dev/v4l/by-path/...`, sem nepatří.
Prázdná nebo nedostupná volba znamená první dostupnou kameru. Přepínání za běhu
uloženou výchozí kameru nemění.

Po úpravě konfigurace nebo seznamu kamer restartuj službu:

```bash
python3 ~/KlipperScreenCam/launcher.py --check
sudo systemctl restart KlipperScreenCam
```

Změnu motivu, jazyka a textů zvoleného překladu aplikace načítá průběžně.

## Menu a obraz

Menu jsem uspořádal takto: **kamery → vypnout/zapnout obraz → Limity snímků →
naměřené FPS → tlačítka limitu**. Otevřeš ho ozubeným kolem vpravo nahoře a zavřeš
křížkem nebo klepnutím mimo něj. Výběr kamery menu zavře a obraz zapne.

Vypnout obraz skutečně uzavře místní spojení s kamerou. Nezastavuje Crowsnest
ani vzdálený náhled. Při vypnutí se zobrazí přeškrtnutá kamera a text „Obraz vypnut“.
Výběr stejné kamery zároveň slouží k obnovení jejího spojení.

U jediné kamery se může skrýt název nad obrazem. Menu zůstává kvůli vypnutí obrazu
a nastavení FPS dostupné. Dlouhé seznamy se posouvají a názvy kamer se zalamují.

## Snímková frekvence

Jako výchozí používám 15 FPS. Na své tiskárně jsem vyzkoušel plynulý obraz i při
10 FPS, proto má smysl nastavení přizpůsobit tomu, co na kameře sleduješ.

Menu nabízí 10, 20, 30 FPS a Neomezeně. Vlastní číselná hodnota z konfigurace se
přidá mezi tlačítka na správné místo bez duplicit. Pro 15 tedy uvidíš
10 / 15 / 20 v prvním řádku a 30 / Neomezeně ve druhém. Pro 20 se další položka nepřidává.

```ini
[stream]
max_fps = unlimited
```

Konfigurace přijímá celé číslo 1–120 nebo `unlimited`. Změna z menu platí do restartu;
po restartu se vrátí nastavení ze souboru. Vynechané snímky se nepředávají WebKitu,
ale původní stream se z Crowsnestu stále čte. Mainsail se tím neomezuje.

**Zdroj** znamená přijímané FPS, **Předáváno** snímky odeslané WebKitu. Údaje jsou
zaokrouhlené na celé FPS; nejsou měřením skutečně vykreslených snímků.
Podrobnosti najdeš v [návodu k FPS](docs/FPS.cs.md).

## Vzhled a jazyky

`theme = auto` a `language = auto` přebírají nastavení KlipperScreenu. Vlastní jazyk
můžeš zvolit názvem JSON souboru bez přípony, například `language = cs`.
Dalších 30 překladů vedle češtiny a angličtiny jsem připravil s pomocí AI a uvítám
jejich kontrolu rodilými mluvčími. Nejde o oficiální překlady KlipperScreenu.
[Jak upravit nebo přidat jazyk](docs/TRANSLATIONS.cs.md).

## Správa přes Moonraker

Instalátor přidá `KlipperScreenCam` do `moonraker.asvc` bez duplicit, zachová ostatní
služby a před první změnou existujícího souboru vytvoří zálohu. Moonraker sám
nerestartuje. Po instalaci ho ve vhodnou dobu restartuj, aby načetl nový seznam.
Podrobný postup je v [návodu k Moonrakeru](docs/MOONRAKER.cs.md).

## Zhasínání a omezení

Čas zhasnutí dál řídí KlipperScreen. Při `pause_on_dpms = true` se místní stream
odpojí po zjištění uspání, standardně do 20 sekund. Volitelná integrace společného
probuzení předá okamžitou zprávu a zavře černou plochu spořiče KlipperScreenu.
Samostatný softwarový spořič bez DPMS aplikace nesleduje.

Podporuji HTTP(S) MJPEG přes X11. WebRTC, HLS, RTSP, Wayland a přímé otevírání
`/dev/video*` tato verze neřeší. Při tichém zaseknutí kamery může být potřeba vybrat
kameru znovu. Volitelná [akcelerace WebKitu](docs/ACCELERATION.cs.md) nastavuje politiku
vykreslování, nikoli záruku hardwarového dekódování MJPEG.

## Diagnostika a odinstalace

```bash
systemctl status KlipperScreenCam --no-pager
journalctl -u KlipperScreenCam -n 100 --no-pager
python3 ~/KlipperScreenCam/launcher.py --version
bash ~/KlipperScreenCam/scripts/uninstall.sh
```

Odinstalátor odstraní službu a ponechá zdroje, konfiguraci i překlady.
Chyby a návrhy můžeš poslat přes Issues. Připoj verzi, systém, popis problému a
odpovídající část logu. Postup pro přispěvatele je v [CONTRIBUTING.md](CONTRIBUTING.md).
Podrobnosti ověření ponechávám zvlášť v [záznamu ověření](docs/VERIFICATION.cs.md).

Licenci projektu jsem zatím nezvolil.

## Uspání a společné probouzení displejů

Na svém RPi jsem ověřil i provoz po restartu. Dotyk na kterémkoli displeji probudí
oba. Při uspání se místní stream skutečně odpojí, standardně nejpozději do 20 sekund;
při probuzení dostane aplikace okamžitou zprávu. Ručně vypnutý obraz zůstane vypnutý.

Nastavení `pause_on_dpms = true` a `dpms_poll_seconds = 20` patří do `[display]`.
Integraci nainstaluji volbou `--shared-wake` a následně restartuji obě služby.
Postup, zálohy a omezení jsou v [návodu k uspávání](docs/RPI_SLEEP.cs.md).
Aktualizace KlipperScreenu může tuto volitelnou úpravu přepsat.
