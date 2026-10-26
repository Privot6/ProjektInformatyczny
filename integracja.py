"""AeroRun: pobieranie Open-Meteo i integracja z godzinowymi pomiarami GIOŚ."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import requests

TZ = 'Europe/Warsaw'
WEATHER_COLS = ['temperature_2m', 'wind_speed_10m', 'precipitation']
PM_COLS = ['pm25', 'pm10']


def pobierz_pogode(latitude: float, longitude: float, past_days: int = 7, forecast_days: int = 1) -> pd.DataFrame:
    """Pobiera godzinową pogodę z Open-Meteo; zwraca czas świadomy strefy."""
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {'latitude': latitude, 'longitude': longitude,
              'hourly': ','.join(WEATHER_COLS), 'past_days': past_days,
              'forecast_days': forecast_days, 'timezone': TZ}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    hourly = response.json().get('hourly', {})
    if not all(k in hourly for k in ['time', *WEATHER_COLS]):
        raise ValueError('Odpowiedź Open-Meteo nie zawiera wymaganych pól godzinowych')
    df = pd.DataFrame({'timestamp': hourly['time'], **{k: hourly[k] for k in WEATHER_COLS}})
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(TZ, ambiguous='NaT', nonexistent='NaT')
    return df.dropna(subset=['timestamp']).sort_values('timestamp').drop_duplicates('timestamp')


def wczytaj_gios(path: str | Path, source_timezone: str = TZ) -> pd.DataFrame:
    """Wczytuje przygotowane przez moduł GIOŚ dane w formacie tabelarycznym CSV/JSON.

    Wymagane pola: timestamp, pm25, pm10. Dopuszczalne aliasy: date, PM2.5, PM10.
    Dla czasu bez strefy zakłada source_timezone (domyślnie Europe/Warsaw).
    """
    path = Path(path)
    if path.suffix.lower() == '.csv':
        df = pd.read_csv(path)
    elif path.suffix.lower() == '.json':
        payload = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(payload, dict) and 'records' in payload:
            payload = payload['records']
        df = pd.DataFrame(payload)
    else:
        raise ValueError('Obsługiwane formaty GIOŚ: CSV i JSON')
    aliases = {'date': 'timestamp', 'time': 'timestamp', 'PM2.5': 'pm25',
               'PM10': 'pm10', 'pm2_5': 'pm25', 'pm2.5': 'pm25'}
    df = df.rename(columns=aliases)
    required = ['timestamp', *PM_COLS]
    missing = [k for k in required if k not in df.columns]
    if missing:
        raise ValueError(f'Brak kolumn w danych GIOŚ: {missing}. Wymagane: {required}')
    df = df[required].copy()
    def parse_timestamp(value):
        if pd.isna(value):
            return pd.NaT
        ts = pd.Timestamp(value)
        if ts.tzinfo is None:
            try:
                ts = ts.tz_localize(source_timezone, ambiguous='NaT', nonexistent='NaT')
            except (ValueError, TypeError):
                return pd.NaT
        return ts.tz_convert(TZ)
    df['timestamp'] = pd.to_datetime(df['timestamp'].map(parse_timestamp), utc=True).dt.tz_convert(TZ)
    for col in PM_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[df[col] < 0, col] = float('nan')
    return df.dropna(subset=['timestamp']).sort_values('timestamp').groupby('timestamp', as_index=False)[PM_COLS].mean()


def polacz_dane(gios: pd.DataFrame, weather: pd.DataFrame, interpolate_limit: int = 2) -> pd.DataFrame:
    """Łączy pomiary godzinowe; interpoluje wyłącznie krótkie luki pomiarowe.

    Nie interpoluje pomiędzy obserwacjami oddalonymi o wiele godzin.
    Zachowuje tylko godziny z kompletnymi pomiarami PM i pogodą.
    """
    a = gios.copy()
    b = weather.copy()
    for frame in (a, b):
        frame['timestamp'] = pd.to_datetime(frame['timestamp'], utc=True).dt.tz_convert(TZ).dt.floor('h')
    a = a.groupby('timestamp', as_index=False)[PM_COLS].mean().set_index('timestamp').sort_index()
    b = b.groupby('timestamp', as_index=False)[WEATHER_COLS].mean().set_index('timestamp').sort_index()
    if a.empty:
        raise ValueError('Brak danych GIOŚ do integracji')
    # Pełna siatka godzinowa ograniczona do zakresu GIOŚ, by uwzględnić luki.
    hours = pd.date_range(a.index.min(), a.index.max(), freq='h', tz=TZ)
    a = a.reindex(hours)
    for col in PM_COLS:
        a[col] = a[col].interpolate(method='linear', limit=interpolate_limit, limit_area='inside')
    combined = a.join(b, how='left')
    combined = combined.dropna(subset=PM_COLS + WEATHER_COLS).reset_index(names='timestamp')
    return combined


def zapisz(df: pd.DataFrame, output_dir: str | Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = output_dir / 'aerorun_dane.csv', output_dir / 'aerorun_dane.json'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    json_path.write_text(df.to_json(orient='records', date_format='iso', force_ascii=False, indent=2), encoding='utf-8')
    return csv_path, json_path


def main():
    parser = argparse.ArgumentParser(description='Integracja danych Open-Meteo i GIOŚ dla AeroRun')
    parser.add_argument('--gios', required=True, help='Ścieżka do pliku GIOŚ CSV/JSON')
    parser.add_argument('--lat', type=float, default=50.0413, help='Szerokość geograficzna stacji')
    parser.add_argument('--lon', type=float, default=21.9990, help='Długość geograficzna stacji')
    parser.add_argument('--gios-timezone', default=TZ, help='Strefa czasowa dat GIOŚ bez offsetu')
    parser.add_argument('--output', default='wyniki', help='Katalog wynikowy')
    args = parser.parse_args()
    gios = wczytaj_gios(args.gios, args.gios_timezone)
    weather = pobierz_pogode(args.lat, args.lon)
    merged = polacz_dane(gios, weather)
    csv_path, json_path = zapisz(merged, args.output)
    print(f'Zapisano {len(merged)} kompletnych rekordów: {csv_path}, {json_path}')
    if len(merged) < 48:
        print('UWAGA: mniej niż 48 wspólnych godzin; sprawdź zakres dat, współrzędne i kompletność GIOŚ.')

if __name__ == '__main__':
    main()
