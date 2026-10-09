import json
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATEI = Path("raumtemps.json")  # hier werden die Datensätze gespeichert

app = FastAPI(title="Raumtemperatur-API")


# So muss der JSON-Body eines POST aussehen: {"ort": "Raum 2.18", "temp": 21.5}
class Messwert(BaseModel):
    ort: str
    temp: float


def laden():
    """Gespeicherte Datensätze beim Start aus der Datei lesen."""
    if DATEI.is_file():
        return json.loads(DATEI.read_text())
    return []


def speichern():
    """Alle Datensätze in die Datei schreiben."""
    DATEI.write_text(json.dumps(raumtemps, indent=2))


raumtemps = laden()  # Liste von Dictionaries, unsere "Datenbank"


# GET /raumtemps  -> alle Datensätze
@app.get("/raumtemps")
def alle_lesen():
    return raumtemps


# GET /raumtemps/2  -> ein Datensatz
@app.get("/raumtemps/{id}")
def einen_lesen(id: int):
    for datensatz in raumtemps:
        if datensatz["id"] == id:
            return datensatz
    raise HTTPException(status_code=404, detail=f"Datensatz mit der id {id} existiert nicht")


# POST /raumtemps  -> neuen Datensatz anlegen
@app.post("/raumtemps", status_code=201)
def anlegen(messwert: Messwert):
    neue_id = max((d["id"] for d in raumtemps), default=0) + 1
    datensatz = {
        "id": neue_id,
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ort": messwert.ort,
        "temp": messwert.temp,
    }
    raumtemps.append(datensatz)
    speichern()
    print("Empfangen:", datensatz)  # Anzeige in der Server-Konsole
    return datensatz


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
