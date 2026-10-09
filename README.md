# LF7 REST-Webserver (Raumtemperatur-API)

Kleiner REST-Server mit FastAPI, um GET- und POST-Anfragen auszuprobieren.

## Endpunkte

| Methode | Pfad              | Beschreibung              |
|---------|-------------------|---------------------------|
| GET     | `/raumtemps`      | alle Datensätze           |
| GET     | `/raumtemps/{id}` | einen Datensatz           |
| POST    | `/raumtemps`      | neuen Datensatz anlegen   |

Beispiel-Body für POST: `{"ort": "Raum 2.18", "temp": 21.5}`

Die interaktive API-Doku gibt es unter `http://<IP>:8080/docs`.

## Server starten

```bash
cd restserver
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py
```

## Testen

```bash
curl http://localhost:8080/raumtemps
curl -X POST http://localhost:8080/raumtemps \
     -H "Content-Type: application/json" \
     -d '{"ort": "Raum 2.18", "temp": 21.5}'
```
