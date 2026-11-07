def high_pm_cases(cfg):

    for case, pm25, pm10 in [('high_pm25', 2*cfg['pm25_scale'], 0.),
                             ('high_pm10', 0., 2*cfg['pm10_scale'])]:
        yield case, dict(pm25=pm25, pm10=pm10, temperature_2m=15.,
                         wind_speed_10m=5., precipitation=0.)
