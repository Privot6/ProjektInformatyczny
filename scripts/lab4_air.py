import math

def check_pm(row):
    values = {}
    for key in ('pm25', 'pm10'):
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'Brak lub błędne {key}') from exc
        if not math.isfinite(value) or value < 0:
            raise ValueError(f'{key}: wymagana skończona wartość >= 0')
        values[key] = value

    return values

def summarize_pm(rows):
    checked = [check_pm(row) for row in rows]
    if not checked:
        raise ValueError('Pusta próbka PM')
    return {
        'n': len(checked),
        'unit': 'ug/m3',
        'pm25_min': min(r['pm25'] for r in checked),
        'pm25_max': max(r['pm25'] for r in checked),
        'pm10_min': min(r['pm10'] for r in checked),
        'pm10_max': max(r['pm10'] for r in checked),
        'pm25_above_pm10_review_count': sum(r['pm25'] > r['pm10'] for r in checked),
        'missing_policy': 'reject; no interpolation in Lab 4',
        'data_kind': 'GIOS measurements and Open-Meteo ERA5 reanalysis',
    }
