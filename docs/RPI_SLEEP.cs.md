# RPi: společné probuzení a zastavení obrazu při uspání

[English](RPI_SLEEP.md) · [Česky](RPI_SLEEP.cs.md)

Společné probouzení displejů a zastavení místního streamu při uspání jsem ověřil
na Raspberry Pi 5 s Debianem 13 a X11, včetně restartu RPi. Tyto změny jsou
součástí připraveného balíčku 0.3.0; na GitHub je nahraji samostatně.

## Chování

- Čas zhasnutí dál řídí KlipperScreen, například 300 sekund.
- KlipperScreenCam při zjištění uspání DPMS skutečně uzavře místní přenos kamery.
- Uspání kontroluje po 20 sekundách, takže přenos může po zhasnutí ještě tuto dobu běžet.
- Probuzení předá KlipperScreen místní zprávou `wake` do pojmenované roury FIFO.
- Příjem zprávy obnoví stejnou kameru a nastavený limit, pokud obraz před uspáním běžel.
- Ručně vypnutý obraz zůstane vypnutý. Ostatní diváci včetně Mainsailu zůstávají nezávislí.
- Kontrola DPMS po 20 sekundách slouží i jako záloha, pokud zpráva o probuzení nedorazí.

Není tu další časovač zhasínání ani simulované klikání do ovládání tiskárny.
DPMS se čte přímo přes knihovny X11. Pokud ho systém nepodporuje, aplikace to zapíše
do logu a automatické zastavení se nepoužije. Softwarový spořič bez DPMS tato volba nesleduje.

## Nastavení

Do existující sekce `[display]` v KlipperScreenCam.conf patří:

```ini
[display]
pause_on_dpms = true
dpms_poll_seconds = 20
```

Starší zápis v [stream] zůstává dočasně podporovaný a aplikace upozorní v logu.
Při přesunu řádky ze sekce [stream] odstraň; stejné volby nesmějí být v obou sekcích.
max_fps a start_paused ponech v [stream].

Stejné hodnoty platí i při vynechání voleb ze starší konfigurace. Interval může být
1–120 sekund; pro delší interval nastav například 30. `pause_on_dpms = false`
automatické zastavení vypne. Po změně konfigurace restartuj KlipperScreenCam.
Není potřeba upravovat jazyky: změna nepřidává nové texty do rozhraní.

## Co dělá volba --shared-wake

Instalátor s touto výslovnou volbou zkontroluje oba soubory KlipperScreenu před změnou:

- screen.py: při návratu DPMS do On zavře černou plochu spořiče.
- ks_includes/widgets/screensaver.py: po zavření spořiče pošle zprávu kamerovému náhledu.

Úprava odpovídá podobě zdrojů ověřené na mé tiskárně. Při odlišném kódu se zastaví
bez změny těchto souborů. Existující opravu znovu nevkládá. Před změnou vytváří
zálohy s názvem *.before-ksc-shared-wake-DATUM-CAS. KlipperScreen sám nerestartuje.
Aktualizace KlipperScreenu může tyto úpravy přepsat; potom je potřeba integraci znovu zkontrolovat.

Samostatná kontrola a aplikace:

```bash
python3 ~/KlipperScreenCam/scripts/shared_wake.py --directory ~/KlipperScreen
python3 ~/KlipperScreenCam/scripts/shared_wake.py --directory ~/KlipperScreen --apply
```

Zpráva používá `/run/user/UID/KlipperScreenCam/wake.fifo`, případně adresář podle
XDG_RUNTIME_DIR. Roura má práva 0600, její adresář 0700. Zápis KlipperScreenu je
neblokující; zastavený kamerový náhled proto nezablokuje probuzení KlipperScreenu.
Obě aplikace musí běžet pod stejným účtem a se stejným XDG_RUNTIME_DIR.

## Nasazení na existující instalaci

Přenes přiložený KlipperScreenCam-0.3.0.tar.gz do /home/horejsi. Příkazy spusť na
RPi jako horejsi, nikoli na jiném serveru. Ve vhodnou dobu mimo tisk:

```bash
sudo systemctl stop KlipperScreenCam
ksc_backup=$(mktemp -d "$HOME/KlipperScreenCam-before-dpms.XXXXXX")
cp -a ~/KlipperScreenCam "$ksc_backup/project"
cp -p ~/printer_data/config/KlipperScreenCam.conf "$ksc_backup/config.conf"
printf 'Zaloha: %s\n' "$ksc_backup"
cd ~
tar -xzf KlipperScreenCam-0.3.0.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps --shared-wake
python3 launcher.py --check
```

Pokud instalace nebo kontrola skončí chybou, další kroky neprováděj a přečti hlášení.
Při úspěchu načti úpravy KlipperScreenu a spusť kamerový náhled:

```bash
sudo systemctl restart KlipperScreen
sudo systemctl start KlipperScreenCam
systemctl is-active KlipperScreenCam
journalctl -u KlipperScreenCam --since "2 minutes ago" --no-pager
```

Očekávám `DPMS sleep monitoring enabled on :0`. Pokud log hlásí nedostupné DPMS
nebo wake notifications, pošli příslušné hlášení. Instalátor zachová konfiguraci,
rozložení displejů a dotyky. Moonraker není kvůli této změně potřeba restartovat.

## Načtení změn a okamžité probuzení

Po aplikaci integrace restartuj **obě služby**, jak ukazují příkazy výše.
Nestačí restartovat jen kamerový náhled: KlipperScreen musí načíst nový kód
odesílající zprávu o probuzení. Bez něj se obraz může obnovit až při další
pravidelné kontrole, standardně do 20 sekund.

Při dotyku očekávám v logu `Wake notification received from local FIFO` a následně
`DPMS display wake`. Obnovení spojení ke kameře může mít vlastní krátkou prodlevu.

## Ověření

1. Zapni obraz a nech monitory uspat jejich běžným časovačem.
2. Po zhasnutí počkej ještě alespoň 20–25 sekund. V logu má být `DPMS display sleep`
   a uzavření místního kamerového spojení. Ověř CPU a spojení hlavního procesu.
3. Dotkni se kamerového displeje. Oba displeje mají ožít, v logu se objeví
   `Wake notification received` a `DPMS display wake`; stejná kamera se znovu připojí.
4. Zopakuj probuzení dotykem na KlipperScreenu.
5. Ručně vypni obraz, nech displeje uspat a probuď je. Obraz musí zůstat ručně vypnutý.
6. Ověř, že Mainsail i během uspání dál zobrazuje kameru.

```bash
journalctl -u KlipperScreenCam --since "5 minutes ago" --no-pager |
  grep -E 'DPMS|Wake notification|Local camera connection'
ksc_pid=$(systemctl show KlipperScreenCam -p MainPID --value)
sudo ss -tnp | grep "pid=$ksc_pid," || echo "Zadne TCP spojeni hlavniho procesu."
```

Při správném vypnutí nezůstane hlavnímu procesu kamerové TCP spojení. Jiné procesy
mohou dál používat kamery, například otevřený Mainsail.

## Návrat

Nejprve zastav KlipperScreenCam. Obnov projekt a konfiguraci z vypsané zálohy;
nový projekt si ponech pod jiným názvem. Pokud chceš vrátit i úpravy KlipperScreenu,
obnov jen příslušné dva soubory z jejich vypsaných záloh a restartuj KlipperScreen.
Samotné `pause_on_dpms = false` vypne automatické řízení streamu bez návratu zdrojů.
