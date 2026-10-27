# LF7 REST-Webserver (Raumtemperatur-API)

Kleiner REST-Server mit FastAPI und uvicorn, um GET-, POST- und DELETE-Anfragen auszuprobieren. Entstanden für den Workshop "Webserver-Engine mit Python und curl".

* **Interaktives Laborheft als PDF** (IP-Adressen eintragen, `curl`-Befehle passen sich an): [LABORHEFT_interaktiv.pdf](LABORHEFT_interaktiv.pdf). Neu erzeugen nach Änderungen am 

## Endpunkte

| Methode | Pfad              | Beschreibung              | Statuscodes   |
|---------|-------------------|---------------------------|---------------|
| GET     | `/raumtemps`      | alle Datensätze           | 200           |
| GET     | `/raumtemps/{id}` | einen Datensatz           | 200, 400, 404 |
| POST    | `/raumtemps`      | neuen Datensatz anlegen   | 201, 400      |
| DELETE  | `/raumtemps/{id}` | Datensatz löschen         | 200, 400, 404 |

Beim POST gibt es zwei Verfahren (nicht mischen):

* URL-Parameter: `POST /raumtemps?temp=25.9&ort=Raum%202.18`
* JSON-Body: `{"ort": "Raum 2.18", "temp": 25.9}` mit Header `Content-Type: application/json`

Pflicht sind `ort` und `temp`, optional ist `sensor`. Die Datensätze liegen in `restserver/raumtemps.json`.

## Server starten

Linux / Raspberry Pi:

```bash
bash setup.sh                    # einmalig: venv anlegen und Pakete installieren
cd restserver
source .venv/bin/activate
python server.py
```

Windows (PowerShell):

```powershell
cd restserver
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

Getestet mit Python 3.13, FastAPI 0.162 und uvicorn 0.54. Die automatische Endpunkt-Übersicht von FastAPI gibt es unter `http://<IP>:8080/docs`.

## Beispiele zum Testen

```bash
curl http://localhost:8080/raumtemps
curl http://localhost:8080/raumtemps/1
curl -X POST "http://localhost:8080/raumtemps?temp=25.9&ort=Raum%202.18"
curl -X POST http://localhost:8080/raumtemps \
     -H "Content-Type: application/json" \
     -d '{"ort": "Raum 2.18", "temp": 21.5}'
curl -X DELETE http://localhost:8080/raumtemps/1
```

Unter Windows PowerShell `curl.exe` verwenden und den JSON-Body aus einer Datei senden (`--data-binary "@datei.json"`), siehe Laborheft. Fertige Anfragen für die VS-Code-Erweiterung *REST Client* stehen in `restserver/anfragen.http`.
