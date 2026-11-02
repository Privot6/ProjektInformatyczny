"""Mamdani min/max i centroid z gotowych funkcji scikit-fuzzy.

Trzy kompletne reguły na czterech wejściach; parametry demonstracyjne w JSON.
"""
import json, math
from pathlib import Path
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from scripts.lab4_air import check_pm
from scripts.lab4_data import check_weather

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / 'config/lab4.json'

def load_config(path=DEFAULT_CONFIG):
    cfg = json.loads(Path(path).read_text(encoding='utf-8'))
    for key in ('pm25_scale', 'pm10_scale', 'perturbation_pm25', 'sensitivity_pm25_scale'):
        if not math.isfinite(cfg[key]) or cfg[key] <= 0:
            raise ValueError(f'Niepoprawne {key}')
    for key in ('pollution', 'thermal', 'wind', 'rain'):
        a, b, c = cfg['anchors'][key]
        cap = cfg['caps'][key]
        if not all(math.isfinite(x) for x in (a, b, c, cap)) or not 0 <= a < b < c <= cap:
            raise ValueError(f'Niepoprawne funkcje przynależności {key}')
    if not 0 < cfg['labels']['stay_below'] < cfg['labels']['train_from'] < 100:
        raise ValueError('Niepoprawne progi etykiet')
    return cfg

def features(row, cfg):
    pm, weather = check_pm(row), check_weather(row)
    return {
        'pollution': max(pm['pm25'] / cfg['pm25_scale'], pm['pm10'] / cfg['pm10_scale']),
        'thermal': abs(weather['temperature_2m'] - cfg['temperature_center']),
        'wind': weather['wind_speed_10m'], 'rain': weather['precipitation'],
    }

def memberships(value, anchors, cap):
    a, b, c = anchors
    # Funkcje odcinkowo liniowe, siatka zawiera wszystkie ich węzły.
    universe = np.unique(np.array([0., a, b, c, cap]))
    x = min(max(value, 0.), cap)
    return np.array([
        fuzz.interp_membership(universe, fuzz.trapmf(universe, [0, 0, a, b]), x),
        fuzz.interp_membership(universe, fuzz.trimf(universe, [a, b, c]), x),
        fuzz.interp_membership(universe, fuzz.trapmf(universe, [b, c, cap, cap]), x),
    ])

def label(score, cfg):
    if score < cfg['labels']['stay_below']:
        return 'ZOSTAŃ W DOMU'
    if score < cfg['labels']['train_from']:
        return 'OGRANICZ WYSIŁEK'
    return 'TRENUJ'

class FuzzyModel:
    def __init__(self, cfg):
        self.cfg = cfg
        inputs = []
        for key, anchors in cfg['anchors'].items():
            a, b, c = anchors
            cap = cfg['caps'][key]
            universe = np.unique(np.array([0., a, b, c, cap]))
            variable = ctrl.Antecedent(universe, key)
            variable['good'] = fuzz.trapmf(universe, [0, 0, a, b])
            variable['middle'] = fuzz.trimf(universe, [a, b, c])
            variable['bad'] = fuzz.trapmf(universe, [b, c, cap, cap])
            inputs.append(variable)
        score = ctrl.Consequent(np.arange(0., 101.), 'score')
        score['low'] = fuzz.trimf(score.universe, [0, 0, 30])
        score['middle'] = fuzz.trimf(score.universe, [20, 50, 80])
        score['high'] = fuzz.trimf(score.universe, [70, 100, 100])
        score.defuzzify_method = 'centroid'
        bad = inputs[0]['bad']
        not_bad = inputs[0]['good'] | inputs[0]['middle']
        middle = inputs[0]['middle']
        good = inputs[0]['good']
        for variable in inputs[1:]:
            bad = bad | variable['bad']
            not_bad = not_bad & (variable['good'] | variable['middle'])
            middle = middle | variable['middle']
            good = good & variable['good']
        system = ctrl.ControlSystem([
            ctrl.Rule(bad, score['low']),
            ctrl.Rule(not_bad & middle, score['middle']),
            ctrl.Rule(good, score['high']),
        ])
        self.simulation = ctrl.ControlSystemSimulation(system, clip_to_bounds=False)

    def evaluate(self, row):
        cfg = self.cfg
        values = features(row, cfg)
        mu = np.array([memberships(value, cfg['anchors'][key], cfg['caps'][key])
                       for key, value in values.items()])
        good, middle, bad = mu[:, 0], mu[:, 1], mu[:, 2]
        # R1 dowolne złe -> niski; R2 wszystkie nie-złe i dowolne średnie -> średni;
        # R3 wszystkie dobre -> wysoki. OR=max, AND=min. "Nie-złe" = dobre OR średnie.
        fires = [float(max(bad)),
                 float(min(min(np.maximum(good, middle)), max(middle))),
                 float(min(good))]
        if not max(fires):
            raise ValueError('Brak aktywnej reguły')
        for key, value in values.items():
            self.simulation.input[key] = min(value, cfg['caps'][key])
        self.simulation.compute()
        score = float(self.simulation.output['score'])
        return {'score': score, 'label': label(score, cfg),
                'r_bad': fires[0], 'r_middle': fires[1], 'r_good': fires[2]}

def baseline(row, cfg):
    grades = []
    for key, value in features(row, cfg).items():
        a, b, c = cfg['anchors'][key]
        grades.append(90. if value <= (a+b)/2 else 50. if value <= (b+c)/2 else 10.)
    score = min(grades)
    return {'score': score, 'label': label(score, cfg)}
