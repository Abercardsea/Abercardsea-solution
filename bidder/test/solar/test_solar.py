from bidder.src.solar import get_solar_prediction
import numpy as np
import pandas as pd

def test_get_solar_prediction(timeseries):
    expected = np.array([
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0.73533458,
        22.10395128,
        73.48282556,
        128.46069879,
        171.01085531,
        105.54521388,
        22.86610925,
        24.82688955,
        26.33028684,
        27.44334309,
        28.21967379,
        86.49543662,
        144.87076933,
        145.3642569,
        144.82108437,
        143.56684068,
        142.3922313,
        85.01084492,
        28.07342403,
        27.82977723,
        27.51624032,
        27.07021718,
        26.39893834,
        25.4549302,
        24.19519125,
        22.57404735,
        20.53115659,
        17.9709704,
        14.72855509,
        10.5417798,
        5.36461416,
        1.27809225,
        0,
        0,
        0,
        0,
        0,
        0
    ])
    series = pd.read_csv('bidder/test/samples/met_office.csv')
    print(series)
    result = get_solar_prediction(series)
    # arange in time
    print(result)
    assert all(np.isclose(result["SolarPower"], expected))
