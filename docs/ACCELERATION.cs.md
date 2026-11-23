# Hardwarová akcelerace WebKitu

[English](ACCELERATION.md) · [Česky](ACCELERATION.cs.md)

Při ladění zátěže CPU jsem přidal volbu politiky vykreslování WebKitu. Na své tiskárně jsem vyzkoušel režim on; výchozí off ponechávám kvůli kompatibilitě s různými grafickými ovladači. Tato volba sama nepotvrzuje hardwarové dekódování MJPEG.

Od 0.2.2 je v KlipperScreenCam.conf podporovaná tato volba:

```ini
[display]
hardware_acceleration = off
```

| Hodnota | Politika WebKitu | Význam |
| --- | --- | --- |
| off | NEVER | Akcelerace vykreslování zakázaná; dosavadní chování. |
| auto | ON_DEMAND | WebKit ji zapne podle požadavků obsahu. |
| on | ALWAYS | WebKit ji bude požadovat trvale. |

Bez uvedení parametru se použije off, aby aktualizace nezměnila funkční instalaci.
Název hodnoty se neodvíjí od motivu ani od Mainsailu. Parametr se načítá při startu aplikace.

Režim off jsem ponechal jako výchozí pro kompatibilitu, nikoli jako doloženou
nutnost pro každý Raspberry Pi. Na konkrétním zařízení má smysl porovnat on proti off.

**Jde o politiku vykreslování WebKitu, nikoliv přímý přepínač hardwarového MJPEG dekodéru.**
Skutečné použití GPU závisí na ovladači a grafické relaci. Log potvrzuje požadovanou
politiku; sám o sobě není důkazem, že GPU skutečně pracuje. Zapnutí nemusí snížit CPU
a nezvyšuje ani nesnižuje rozlišení nebo FPS kamery.

Zdroj významu voleb: [WebKitGTK HardwareAccelerationPolicy](https://webkitgtk.org/reference/webkit2gtk/stable/enum.HardwareAccelerationPolicy.html).

## Porovnání na RPi

1. Použij aktuální instalaci; postup aktualizace je v UPDATE.cs.md. Zachovej konfiguraci a pro první měření nastav off.
2. Vyber stejnou kameru, zapni obraz a ponech stejný počet ostatních diváků jako při dalším měření.
3. Po několika sekundách ustálení zaznamenej CPU:

   ```bash
   top -b -d 1 -n 2 -w 160 |
     awk '/^top -/{sample++} sample==2 {print; if (++lines==25) exit}'
   ```

4. V existující sekci display v souboru printer_data/config/KlipperScreenCam.conf nastav:

   ```ini
   hardware_acceleration = on
   ```

5. Ověř konfiguraci a restartuj jen kamerové rozhraní:

   ```bash
   python3 ~/KlipperScreenCam/launcher.py --check
   sudo systemctl restart KlipperScreenCam
   journalctl -u KlipperScreenCam -n 40 --no-pager
   ```

6. Log má uvést `WebKit hardware acceleration requested: on`. Ověř obraz, kolečko/menu,
   dotyk a vypnutí/zapnutí streamu. Měř se stejnou kamerou a zapnutým obrazem, ne v pauze.
7. Stejným příkazem změř CPU. Krátký vzorek kolísá; porovnej několik vzorků obou režimů.

Zapisuj celkové využití CPU (100 minus idle) i jednotlivé procesy. Na čtyřjádrovém RPi5
30 % jednoho procesu ve výchozím režimu top odpovídá přibližně 7,5 % celé kapacity CPU.
Sleduj i plynulost a případné grafické chyby; pouhý pokles jednoho procesu není celý výsledek.

## Návrat při černém obrazu nebo horším výsledku

Přes SSH vrať hardware_acceleration na off a restartuj KlipperScreenCam.
Není potřeba restartovat Klipper, Crowsnest nebo RPi ani měnit ovladače a boot konfiguraci.
Pokud režim on nenaběhne, k hlášení chyby mi přilož log a aktuální nastavení grafiky. Vyhni se náhodným
změnami oprávnění k /dev/dri nebo vypínáním bezpečnostních funkcí.

Volba akcelerace nemění skutečné vypnutí streamu: místní síťové spojení dál vlastní
Python a při vypnutí jej uzavře. Na mém RPi režim on běžel. Samostatné měření skutečného využití GPU nemám.
