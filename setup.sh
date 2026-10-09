#!/bin/bash
set -e   # bei einem Fehler bricht das Skript ab.

cd ~/Desktop/LF7_Rest_Webserver/restserver

echo "Erstelle virtuelle Umgebung (venv): eigenes Python, damit die Pakete nicht systemweit installiert werden ..."
python3 -m venv venv

venv/bin/pip install -r requirements.txt

clear

echo "Fertig! Zum Starten musst du folgendes Ausfuehren:"
echo "  cd ~/Desktop/LF7_Rest_Webserver/restserver"
echo "  source venv/bin/activate -> aktiviert die virtuelle Python Umgebung"
echo "  python server.py -> Um den Server zu Starten"