"""Zapis niezmodyfikowanej odpowiedzi API i godzinowej próbki CSV."""
import argparse, json
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
import requests

p=argparse.ArgumentParser()
p.add_argument('--lat',type=float,default=50.0413)
p.add_argument('--lon',type=float,default=21.9990)
p.add_argument('--output',default='data/raw')
a=p.parse_args()
url='https://api.open-meteo.com/v1/forecast'
params={'latitude':a.lat,'longitude':a.lon,'hourly':'temperature_2m,wind_speed_10m,precipitation','past_days':7,'forecast_days':1,'timezone':'UTC'}
r=requests.get(url,params=params,timeout=30); r.raise_for_status(); payload=r.json()
if not all(k in payload.get('hourly',{}) for k in ['time','temperature_2m','wind_speed_10m','precipitation']): raise ValueError('Niekompletna odpowiedź API')
out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
(out/'open_meteo_odpowiedz_api.json').write_text(json.dumps({'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'request_url':r.url,'response':payload},ensure_ascii=False,indent=2),encoding='utf-8')
h=payload['hourly']; timestamps=pd.to_datetime(h['time']).tz_localize('UTC').tz_convert('Europe/Warsaw'); pd.DataFrame({'timestamp':timestamps.strftime('%Y-%m-%dT%H:%M:%S%z'),**{k:h[k] for k in ['temperature_2m','wind_speed_10m','precipitation']}}).to_csv(out/'open_meteo_api.csv',index=False)
print('Zapisano rzeczywistą odpowiedź API i CSV. CSV zawiera jednoznaczny offset Europe/Warsaw, również podczas zmiany czasu.')
