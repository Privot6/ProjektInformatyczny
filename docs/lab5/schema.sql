PRAGMA foreign_keys = ON;

CREATE TABLE source_capture (
    source TEXT PRIMARY KEY CHECK (source IN ('ios_pib_pm10', 'open_meteo')),
    retrieved_at_utc TEXT NOT NULL
) STRICT;

CREATE TABLE forecast_day (
    local_date TEXT PRIMARY KEY,
    pm10_daily_mean REAL CHECK (pm10_daily_mean >= 0),
    missing_weather_hours INTEGER NOT NULL CHECK (missing_weather_hours BETWEEN 0 AND 25)
) STRICT;

CREATE TABLE forecast_hour (
    timestamp_utc INTEGER PRIMARY KEY CHECK (timestamp_utc % 3600 = 0),
    local_date TEXT NOT NULL REFERENCES forecast_day(local_date),
    temperature_2m REAL CHECK (temperature_2m BETWEEN -90 AND 60),
    precipitation REAL CHECK (precipitation >= 0),
    wind_speed_10m REAL CHECK (wind_speed_10m >= 0)
) STRICT;

CREATE INDEX forecast_hour_by_date ON forecast_hour (local_date, timestamp_utc);
