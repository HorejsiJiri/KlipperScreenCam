# Správa KlipperScreenCam přes Moonraker

## Ovládání služby přes Moonraker

Instalátor automaticky doplní KlipperScreenCam do seznamu bez duplicit a zachová ostatní položky.
Před první změnou existujícího souboru uloží moonraker.asvc.ksc-backup. Moonraker automaticky
nerestartuje. Pro běžný datový
adresář `~/printer_data` otevři:

```bash
nano ~/printer_data/moonraker.asvc
```

Ponech ostatní řádky a přidej samostatný řádek, pokud už v seznamu není:

```text
KlipperScreenCam
```

Název musí odpovídat velikostí písmen, bez `.service`. Ulož soubor a načti nový seznam:

```bash
sudo systemctl restart moonraker
```

Webové rozhraní může při restartu Moonrakeru krátce ztratit spojení. Tento krok
proveď při prvním nastavení mimo probíhající tisk. U vlastní datové cesty nebo
více instancí použij příslušný datový adresář a název služby Moonrakeru.

Restart náhledu přes místní API Moonrakeru:

```bash
curl --fail-with-body -sS -X POST \
  -H 'Content-Type: application/json' \
  -d '{"service":"KlipperScreenCam"}' \
  http://127.0.0.1:7125/machine/services/restart
```

Úspěšná odpověď obsahuje `"result":"ok"`. Ověř běh přes
`systemctl is-active KlipperScreenCam`. Podle klienta může být služba dostupná také
v nabídce systémových služeb Mainsailu; ověř to v konkrétní verzi rozhraní.
Pokud API vyžaduje autentizaci, použij přihlášeného klienta nebo jeho běžné
přihlašovací údaje; nevypínej autorizaci Moonrakeru. Oprávnění ke správě systémových
služeb musí mít již nastavené samotný Moonraker.

Automatické povolení lze vynechat přes `--skip-moonraker-registration`. Vlastní datový
adresář zadej přes `--moonraker-data-dir /cesta/printer_data`; jinak se použije nadřazený
adresář `--config-dir`. Výše uvedená ruční úprava slouží ke kontrole nebo doplnění.
Při odinstalaci lze odstranit pouze řádek `KlipperScreenCam` a znovu načíst Moonraker.

Oficiální dokumentace: [povolené služby](https://moonraker.readthedocs.io/en/latest/configuration/#allowed-services)
a [restart přes API](https://moonraker.readthedocs.io/en/latest/external_api/machine/#restart-a-system-service).
