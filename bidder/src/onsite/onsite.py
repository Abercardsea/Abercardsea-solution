"""This file contains functions that return the energy demand of the office site."""

import datetime
import numpy as np
import pandas as pd

from typing import List

from bidder.src.common import interp_30min
from bidder.src.onsite.utils import get_temperatures, temp_to_energy, adjust_datetime
from bidder.src.onsite.utils import create_initial_demand_dataframe, get_active_office_mask
from sqlalchemy import create_engine



def get_energy_demand(
    forecast: pd.DataFrame,
    start_time=datetime.datetime.now().replace(hour=23, minute=0, second=0),
) -> pd.DataFrame:
    """Get the energy demand for the building.

    Returns the total energy demand for the building over the next 24 hours,
    in 30 minute intervals.

    Args:
        forecast (dict): Forcast dataframe.
        start_time (datetime.datetime): The datetime to start predicting building demand from.

    Returns: pd.DataFrame: The total energy demand for the building over the next
        24 hours, in 30 minute intervals (48 instances).
    """
    #forecast = interp_30min(forecast) no longer needed
    start_time = adjust_datetime(start_time)

    demand_dataframe = create_initial_demand_dataframe(start_time)

    active_office_mask = get_active_office_mask(start_time)

    temperatures_over_coming_24_hours, heating_demand = get_heating_demand(
        forecast, active_office_mask
    )
    demand_dataframe["Heating"] = heating_demand
    demand_dataframe["HQ Temperature"] = temperatures_over_coming_24_hours
    demand_dataframe["Data Centre"] = get_data_centre_demand()
    demand_dataframe["Office Equipment"] = get_office_equipment_demand(
        active_office_mask
    )
    demand_dataframe["LightingOther"] = get_lighting_and_other_demand(
        active_office_mask
    )

    demand_dataframe["Total demand"] = (
        demand_dataframe["Heating"]
        + demand_dataframe["Data Centre"]
        + demand_dataframe["Office Equipment"]
        + demand_dataframe["LightingOther"]
    )

    return demand_dataframe

def save_to_db_energy(data):
    """Save energy data to database."""
    engine = create_engine("sqlite:///database/llanwrydd.db")
    data.to_sql("onsiteEnergy", engine, if_exists="append", index=False)


def get_heating_demand(
    forecast: pd.DataFrame, active_office_mask: List[bool]
) -> np.ndarray:
    """Get the energy demands for the building's heating system.

    Returns a numpy array of the energy demands of the heating system over
    the next 24 hours, in 30 minute intervals.

    Args:
        forecast (dict): Forcast dataframe.
        active_office_mask (List[bool]): An array of boolean values corresponding to whether
                                         people are in the office or not.

    Returns: np.ndarray: The energy demands of the heating system over the next
        24 hours, in 30 minute intervals (48 instances).
    """
    temperatures_over_coming_24_hours = get_temperatures(forecast)
    heating_demand = np.zeros(48)
    for index, _ in enumerate(heating_demand):
        if active_office_mask[index]:
            heating_demand[index] = temp_to_energy(
                temperatures_over_coming_24_hours[index]
            )

    return temperatures_over_coming_24_hours, heating_demand


def get_data_centre_demand() -> np.ndarray:
    """Get the energy demand for the data center.

    Returns a numpy array with the energy demand of the data centre over the
    coming 24 hour period, in 30 minute intervals. Currently a dummy function.

    Returns: np.ndarray: The energy demands of the data center over the next 24
        hours, in 30 minute intervals (48 instances).
    """
    return np.ones(48) * 200


def get_office_equipment_demand(active_office_mask: List[bool]) -> np.ndarray:
    """Get the energy demand for the building's office equipment.

    Returns a numpy array with the energy demand of the office equipment over
    the coming 24 hour period, in 30 minute intervals.

    Args:
        active_office_mask (List[bool]): An array of boolean values corresponding to whether
                                         people are in the office or not.

    Returns: np.ndarray: The energy demands of the office equipment over the
        next 24 hours, in 30 minutes intervals (48 instances).
    """
    demand = np.zeros(48)
    for index, _ in enumerate(demand):
        if active_office_mask[index]:
            demand[index] = 10
    return demand


def get_lighting_and_other_demand(active_office_mask: List[bool]) -> np.ndarray:
    """Get the energy demand for the building's lighting and miscellaneous equipment.

    Returns a numpy array with the energy demand of the lighting and 'other'
    energy demand over the coming 24 hour period, in 30 minute intervals.

    Args:
        active_office_mask (List[bool]): An array of boolean values corresponding to whether
                                         people are in the office or not.

    Returns: np.ndarray: The energy demands of the lighting and other equipment
        over the next 24 hours, in 30 minutes intervals (48 instances).
    """
    demand = np.zeros(48)
    for index, _ in enumerate(demand):
        if active_office_mask[index]:
            demand[index] = 20
    return demand

if __name__=='__main__':
    

    pass