"""Konsola do pojedynczych prób manualnych, bez asercji i automatycznej oceny.

Uruchom: python -i scripts/manual_lab7.py
Próbka i SQLite są kopiami w katalogu tymczasowym, usuwanymi po wyjściu.
"""
import json
from datetime import date
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
from backend import storage
from backend.main import check
from backend.model import classify, train, training_score
from backend.sources import timestamps

temporary = tempfile.TemporaryDirectory(prefix="aerorun-lab7-")
work = Path(temporary.name)
shutil.copyfile(ROOT / "data/raw/sample.json", work / "sample.json")
sample = json.loads((work / "sample.json").read_text(encoding="utf-8"))
mode = "archive"


def replay(request):
    if mode == "offline":
        return httpx.Response(503)
    key = "ios_pib_pm10" if request.url.host == "api.prognozy.ios.edu.pl" else "open_meteo"
    return httpx.Response(200, json=sample[key])


model, metrics = train()
client = httpx.Client(transport=httpx.MockTransport(replay))
state = SimpleNamespace(model=model, db=work / "manual.sqlite3", backoff={}, client=client)
storage.initialize(state.db)


def show(day, name):
    """Wykonaj operację i zachowaj JSON do ręcznego odczytania."""
    result = check(date.fromisoformat(day), state)
    destination = ROOT / "results/lab7" / (name + ".json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": result["date"], "hours": len(result["hours"]),
                      "pm10": result["pm10_daily_mean"], "best": result["best"],
                      "origin": result["origin"], "warnings": result["warnings"]}, ensure_ascii=False))
    return result


print("Konsola manualna gotowa. mode='archive' lub 'offline'.")
print("Przykład: result = show('2026-11-12', 'M08')")
print("Operator sam porównuje wynik z docs/tests.md. Brak automatycznego PASS/FAIL.")
