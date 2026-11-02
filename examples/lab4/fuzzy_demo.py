"""Minimalna demonstracja gotowych funkcji scikit-fuzzy i modelu projektowego."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.fuzzy_model import FuzzyModel, load_config

model = FuzzyModel(load_config())
row = dict(pm25=5, pm10=10, temperature_2m=15, wind_speed_10m=5, precipitation=0)
result = model.evaluate(row)
assert abs(result['score']-90) < 1e-6
print(result)
print('Kontrola ręczna: centroid trójkąta (70 + 100 + 100)/3 = 90.')
