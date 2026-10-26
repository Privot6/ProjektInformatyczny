"""Powtarzalne przetwarzanie zapisanych próbek AeroRun, bez ponownego pobierania API."""
import argparse
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integracja import wczytaj_gios, polacz_dane, zapisz, WEATHER_COLS, PM_COLS, TZ

def prepare(gios_path, weather_path, output_dir):
    gios = wczytaj_gios(gios_path)
    raw = pd.read_csv(weather_path)
    required = ['timestamp', *WEATHER_COLS]
    if not set(required).issubset(raw.columns):
        raise ValueError('Brak wymaganych pól pogody')
    if raw['timestamp'].isna().any():
        raise ValueError('Pusty timestamp w pogodzie')
    weather = raw[required].copy()
    weather['timestamp'] = pd.to_datetime(weather['timestamp'], utc=True, errors='raise').dt.tz_convert(TZ)
    for col in WEATHER_COLS:
        weather[col] = pd.to_numeric(weather[col], errors='coerce')
    # Błędne wartości odrzucamy, zamiast ukrywać je w agregacji.
    if weather['timestamp'].duplicated().any():
        raise ValueError('Powtórzony timestamp pogody — kontrola jakości niezaliczona')
    if (weather['wind_speed_10m'].dropna() < 0).any() or (weather['precipitation'].dropna() < 0).any():
        raise ValueError('Ujemny wiatr lub opad — kontrola jakości niezaliczona')
    if weather['temperature_2m'].dropna().lt(-90).any() or weather['temperature_2m'].dropna().gt(60).any():
        raise ValueError('Temperatura poza zakresem kontroli -90..60 °C')
    weather = weather.sort_values('timestamp').set_index('timestamp')
    # Interpolujemy tylko pojedyncze braki wewnątrz szeregu (nie ekstrapolujemy).
    weather[WEATHER_COLS] = weather[WEATHER_COLS].interpolate(method='time',limit=1,limit_area='inside')
    weather = weather.reset_index()
    merged = polacz_dane(gios, weather)
    if merged.empty:
        raise ValueError('Brak wspólnych kompletnych godzin')
    assert merged['timestamp'].is_unique, 'Duplikaty klucza po połączeniu'
    assert merged['timestamp'].notna().all(), 'Puste daty'
    assert merged[PM_COLS+WEATHER_COLS].notna().all().all(), 'Brakujące dane w wyniku'
    assert merged[PM_COLS+['wind_speed_10m','precipitation']].ge(0).all().all(), 'Ujemne wartości fizyczne'
    assert str(merged['timestamp'].dt.tz) == TZ, 'Niewłaściwa strefa czasowa'
    csv_path,json_path = zapisz(merged, output_dir)
    print(f'GIOŚ po wczytaniu: {len(gios)}; pogoda surowa: {len(raw)}; wynik: {len(merged)}')
    print(f'Braki pogody przed: {raw[WEATHER_COLS].isna().sum().to_dict()}')
    print(f'Braki wyniku: {merged[PM_COLS+WEATHER_COLS].isna().sum().to_dict()}')
    print(f'Zapisano: {csv_path} oraz {json_path}')
    return merged

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--gios',default='data/raw/gios_syntetyczne.csv')
    p.add_argument('--weather',default='data/raw/open_meteo_syntetyczne.csv')
    p.add_argument('--output',default='data/processed')
    a=p.parse_args()
    prepare(a.gios,a.weather,a.output)
