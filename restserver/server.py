import json
import math
import threading
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def fehler(status, problem, nachricht):
    """Einheitliche Fehlerantwort als JSON, z. B. mit Statuscode 400 oder 404."""
    return JSONResponse(
        status_code=status,
        content={"problem": problem, "nachricht": nachricht},
    )


# ---------------------------------------------------------------------------
# Datenhaltung: kennt kein HTTP, verwaltet nur die Datensätze
# ---------------------------------------------------------------------------
class TemperatureStore:
    def __init__(self, dateiname):
        self.filepath = Path(dateiname)
        self.templist = []  # Liste von Dictionaries, unsere "Datenbank"
        self.lock = threading.Lock()  # verhindert, dass zwei Anfragen gleichzeitig schreiben
        self.load()

    def load(self):
        """Gespeicherte Datensätze beim Start aus der Datei lesen."""
        if self.filepath.is_file():
            with self.filepath.open("r", encoding="utf-8") as datei:
                self.templist = json.load(datei)

    def save(self):
        """Alle Datensätze in die Datei schreiben."""
        with self.filepath.open("w", encoding="utf-8") as datei:
            json.dump(self.templist, datei, ensure_ascii=False, indent=2)

    def get_all(self):
        return self.templist

    def get_by_id(self, id):
        for datensatz in self.templist:
            if datensatz["id"] == id:
                return datensatz
        return None

    def append(self, ort, temp, sensor=None):
        with self.lock:
            neue_id = max((d["id"] for d in self.templist), default=0) + 1
            datensatz = {
                "id": neue_id,
                "zeit": datetime.now().isoformat(timespec="seconds"),
                "ort": ort,
                "sensor": sensor,
                "temp": temp,
            }
            self.templist.append(datensatz)
            self.save()
            return datensatz

    def delete(self, id):
        with self.lock:
            datensatz = self.get_by_id(id)
            if datensatz is not None:
                self.templist.remove(datensatz)
                self.save()
            return datensatz


# ---------------------------------------------------------------------------
# HTTP-Verarbeitung: nimmt Anfragen entgegen, prüft sie, ruft den Store auf
# ---------------------------------------------------------------------------
class TemperatureAPI:
    def __init__(self, store):
        self.store = store

    # GET /raumtemps
    def get_all(self):
        return self.store.get_all()

    # GET /raumtemps/2
    def get_one(self, id: int):
        datensatz = self.store.get_by_id(id)
        if datensatz is None:
            return fehler(404, "Datensatz nicht gefunden", f"Die ID {id} existiert nicht.")
        return datensatz

    # POST /raumtemps
    async def post(self, request: Request):
        # Variante A: Parameter wurden an die URL angehängt (?temp=..&ort=..)
        if request.query_params:
            temp = request.query_params.get("temp")
            ort = request.query_params.get("ort")
            sensor = request.query_params.get("sensor")
            if temp is None or ort is None:
                return fehler(400, "Fehlende URL-Parameter",
                              "Die URL-Parameter temp und ort sind erforderlich.")
            return self._anlegen(ort, temp, sensor)

        # Variante B: Parameter wurden als JSON im Body übertragen
        if "application/json" in request.headers.get("content-type", ""):
            try:
                daten = await request.json()
            except ValueError:
                daten = None
            if not isinstance(daten, dict):
                return fehler(400, "Ungültiges JSON", "Es wird ein JSON-Objekt erwartet.")
            temp = daten.get("temp")
            ort = daten.get("ort")
            if temp is None or ort is None:
                return fehler(400, "Fehlende JSON-Parameter",
                              "Im JSON-Body müssen temp und ort enthalten sein.")
            return self._anlegen(ort, temp, daten.get("sensor"))

        return fehler(400, "Keine verwertbaren Daten",
                      "Parameter entweder in der URL oder als JSON senden.")

    def _anlegen(self, ort, temp, sensor):
        """Gemeinsame Prüfung für beide Varianten, danach speichern."""
        ort = str(ort).strip()
        if isinstance(temp, bool):  # in Python ist True auch eine Zahl, hier unerwünscht
            return fehler(400, "Ungültige Temperatur", "temp muss eine Zahl sein.")
        try:
            temp = float(temp)
        except (TypeError, ValueError):
            return fehler(400, "Ungültige Temperatur", "temp muss eine Zahl sein.")
        if not math.isfinite(temp):
            return fehler(400, "Ungültige Temperatur", "temp muss eine endliche Zahl sein.")
        if ort == "":
            return fehler(400, "Ungültiger Ort", "ort darf nicht leer sein.")

        datensatz = self.store.append(ort, temp, sensor)
        print("Empfangen:", datensatz)  # Anzeige in der Server-Konsole
        return JSONResponse(status_code=201, content=datensatz)

    # DELETE /raumtemps/2
    def delete(self, id: int):
        datensatz = self.store.delete(id)
        if datensatz is None:
            return fehler(404, "Datensatz nicht gefunden", f"Die ID {id} existiert nicht.")
        return datensatz


# ---------------------------------------------------------------------------
# Anwendung zusammenbauen
# ---------------------------------------------------------------------------
class TemperatureServer:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Raumtemperatur-API")
        # Die Datei liegt neben server.py, egal von wo der Server gestartet wird.
        self.store = TemperatureStore(Path(__file__).with_name("raumtemps.json"))
        self.api = TemperatureAPI(self.store)
        self._register_routes()

    def _register_routes(self):
        self.app.add_api_route("/raumtemps", self.api.get_all, methods=["GET"])
        self.app.add_api_route("/raumtemps", self.api.post, methods=["POST"], status_code=201)
        self.app.add_api_route("/raumtemps/{id}", self.api.get_one, methods=["GET"])
        self.app.add_api_route("/raumtemps/{id}", self.api.delete, methods=["DELETE"])

        # Ungültige ID (z. B. /raumtemps/abc) soll wie in der Aufgabe als 400 antworten
        @self.app.exception_handler(RequestValidationError)
        async def ungueltige_anfrage(request, exc):
            return fehler(400, "Ungültige Anfrage",
                          "Die ID muss eine ganze Zahl sein, z. B. /raumtemps/1.")

    def run(self):
        uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    TemperatureServer().run()
