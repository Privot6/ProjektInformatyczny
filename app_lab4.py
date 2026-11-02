"""Przegląd historycznego eksperymentu AeroRun Lab 4, bez pobierania danych."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='AeroRun · Lab 4', page_icon='🌿', layout='wide')
st.title('AeroRun — porównanie rekomendacji')
st.caption('Laboratorium 4 · reguły progowe i wnioskowanie rozmyte Mamdaniego')
st.warning('Dane syntetyczne. Etykiety są wynikiem demonstracji algorytmu, bez potwierdzenia bezpieczeństwa treningu.')
scenario = st.radio('Scenariusz', ['Podstawowy', 'Próba wrażliwości'], horizontal=True)
folder = ROOT/'results/lab4'
if scenario == 'Próba wrażliwości':
    folder /= 'sensitivity'
required = [folder/name for name in ('comparison.csv', 'observations.csv', 'run.json')]
if not all(path.exists() for path in required):
    st.info('Brak wyników. Uruchom z katalogu projektu: python scripts/compare_methods.py')
    st.stop()
try:
    comparison = pd.read_csv(required[0])
    observations = pd.read_csv(required[1])
    run = json.loads(required[2].read_text(encoding='utf-8'))
    observations['timestamp'] = pd.to_datetime(observations['timestamp'], utc=True).dt.tz_convert('Europe/Warsaw')
    needed = {'timestamp', 'wariant', 'score', 'label', 'pm25', 'pm10', 'temperature_2m',
              'wind_speed_10m', 'precipitation', 'score_perturbed', 'label_perturbed'}
    if not needed.issubset(observations.columns):
        raise ValueError('Niepełne kolumny observations.csv')
    indexed = comparison.set_index('wariant')
    b = float(indexed.loc['bazowy', 'mean_abs_score_change_points'])
    f = float(indexed.loc['rozmyty', 'mean_abs_score_change_points'])
except (ValueError, KeyError, OSError) as exc:
    st.error(f'Nie można odczytać wyników: {exc}')
    st.stop()

left, middle, right = st.columns(3)
left.metric('Zmiana indeksu — progi', f'{b:.3f} pkt')
middle.metric('Zmiana indeksu — rozmyty', f'{f:.3f} pkt')
right.metric('Liczba godzin', str(int(indexed.loc['bazowy', 'n'])))
st.caption('Średnia bezwzględna zmiana indeksu po zwiększeniu PM2.5 o 1 µg/m³. Mniej oznacza większą stabilność, nie większą trafność.')
st.subheader('Porównanie metod')
st.dataframe(comparison, hide_index=True)
st.write('Kryterium demonstracyjne: ' + ('spełnione' if run['practical_criterion_met'] else 'niespełnione / brak rozstrzygnięcia'))

days = sorted(observations['timestamp'].dt.date.unique())
day = st.selectbox('Dzień obserwacji', days)
selected = observations[observations['timestamp'].dt.date == day].copy()
st.subheader('Oceny godzinowe')
chart = selected.pivot(index='timestamp', columns='wariant', values='score')
st.line_chart(chart, y_label='Indeks 0–100')
st.caption('Wykres pokazuje ocenę pomiarów historycznych, bez prognozy przyszłej doby.')

st.subheader('Najwyżej ocenione godziny w demonstracji')
top = selected[(selected['wariant'] == 'rozmyty') & (selected['label'] == 'TRENUJ')]
top = top.sort_values(['score', 'timestamp'], ascending=[False, True]).head(3)
if top.empty:
    st.info('W tym dniu algorytm rozmyty nie przypisał etykiety TRENUJ.')
else:
    st.dataframe(top[['timestamp', 'score', 'label', 'pm25', 'pm10']], hide_index=True)
st.caption('Do trzech pojedynczych godzin. Nie jest to wyznaczenie ciągłego okna treningowego ani zalecenie zdrowotne.')

with st.expander('Pomiary i wynik perturbacji'):
    st.dataframe(selected, hide_index=True)
with st.expander('Konfiguracja i odtwarzalność'):
    st.json(run)
st.download_button('Pobierz porównanie CSV', required[0].read_bytes(), 'comparison.csv', 'text/csv')
st.download_button('Pobierz obserwacje CSV', required[1].read_bytes(), 'observations.csv', 'text/csv')
