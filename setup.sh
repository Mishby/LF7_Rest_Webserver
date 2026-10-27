#!/bin/bash
set -e   # bei einem Fehler bricht das Skript ab.

# In den Ordner restserver wechseln, egal wo das Repo liegt
cd "$(dirname "$0")/restserver"

echo "Erstelle virtuelle Umgebung (.venv): eigenes Python, damit die Pakete nicht systemweit installiert werden ..."
python3 -m venv .venv

.venv/bin/pip install -r requirements.txt

echo "Fertig! Zum Starten musst du folgendes Ausfuehren:"
echo "  cd restserver"
echo "  source .venv/bin/activate -> aktiviert die virtuelle Python Umgebung"
echo "  python server.py -> Um den Server zu Starten"
