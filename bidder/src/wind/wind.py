# -*- coding: utf-8 -*-
"""
Read in API forecast and output hourly wind power production predictions
for the next 24 between 23:00 and 23:00
Based on SLIMJAB
"""
from datetime import datetime
from typing import Union

import numpy as np
import os
import pandas as pd
import pickle as p

from bidder.src.common import interp_30min
import bidder.src.config as config
from sqlalchemy import create_engine
# load model
root = os.path.dirname(__file__)

wind_model = None
with open(os.path.join(root, "wind_model.pkl"), "rb") as f:
    wind_model = p.load(f)


def get_wind_speed(forecast: pd.DataFrame) -> pd.DataFrame:
    """Unpacks wind speed from forecast.
     Unpacks wind speed in mph from a pd.DataFrame containing forecast data and
     converts it to m/s.
     Args:
        forecast (pd.DataFrame) : MetOffice forecast data.
    Returns:
        pd.DataFrame object containing wind speed and datetime information.
    """
    assert isinstance(forecast, pd.DataFrame)
    # mph to m/s
    forecast["F"] = forecast["F"].apply(lambda x: x * 0.44704)
    return forecast[["DateTime", "F"]].reset_index()


def get_wind_power(
    windspeed: Union[list, np.ndarray, pd.Series, float], height: Union[int, float] = 10
) -> np.ndarray:
    """Converts windspeed to power.
     Converts a windspeed or set of windspeeds at a given height to power
     generated in kW according to the wind model created from the turbine
     datasheets.
     Args:
        windspeed (list, np.ndarray, float  : Windspeed or set of
                   pd.Series)                 windspeeds in m/s.
        height (int, float)                 : Rotor height (default is 10m)
    Returns:
        np.ndarray object corresponding to the power generated (in kW).
    Raises:
        ValueError  : if windspeed < 0
        ValueError  : if height < 0
    """

    n_turbines = 6  # Number of active turbines
    hellman_exp = 0.34  # Hellman exponent for static air above inhabited areas
    assert isinstance(windspeed, (list, np.ndarray, float, pd.Series))
    assert isinstance(height, (int, float))

    if isinstance(windspeed, (list, float, pd.Series)):
        windspeed = np.asarray(windspeed)
    assert np.all(windspeed >= 0)  # Check all windspeeds are non-negative
    assert height >= 0

    correction = (height / 10) ** hellman_exp  # Terrain/height correction

    windspeed *= correction
    windspeed[windspeed >= 30] = 30  # Truncate excess speeds
    return n_turbines * wind_model(windspeed)


def get_wind_prediction(forecast: pd.DataFrame) -> pd.DataFrame:
    """Wrapper function to return array of predicted wind power generation for forecast timesteps.

    Args:
        forecast (dict): Forcast dataframe.

    Returns:
        wind_report (pd.DataFrame): The wind speed and predicted wind energy output of wind turbines over the
    next 24 hours, in 30 minute intervals (48 instances).
    """
    altitude = config.ALTITUDE
    #forecast = interp_30min(forecast) # No-longer needed.
    wind_speed = get_wind_speed(forecast)
    wind_power = get_wind_power(wind_speed["F"], altitude)
    wind_report = pd.DataFrame(
        data={
            "time": wind_speed["DateTime"],
            "WindSpeed": wind_speed["F"],
            "WindPower": wind_power,
        }
    )
    return wind_report.iloc[:-1]

def save_to_db_wind(wind):
    """Save wind data to database."""
    engine = create_engine("sqlite:///database/llanwrydd.db")
    # save to database
    wind.to_sql("windPrediction", con=engine, if_exists="append", index=False)