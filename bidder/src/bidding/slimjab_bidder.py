import random
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text

import numpy as np
import pandas as pd

from bidder.src.bidding.util import get_output_template, register_bidder

def excute_sql_to_df(query):
    '''Execute sql query and return dataframe'''
    # query is a string.
    # returns dataframe.
    # connect to database
    engine = create_engine("sqlite:///database/llanwrytd.db")
    with engine.connect() as con:
        result = con.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
    return df


def _get_power_from_db(start_date, end_date):
    """Get power data from database return sql that will get the data from the database."""
    sql =  "SELECT time, (WindPower + SolarPower - HQPowerDemand) * 1000 AS NetPower FROM powerPrediction WHERE time > "+start_date+" AND time < "+end_date
    return excute_sql_to_df(sql)

def _get_price_from_db(start_date, end_date):
    """Get price data from database return sql that will get the data from the database."""
    sql =  "SELECT * FROM pricePrediction WHERE time > "+start_date+" AND time < "+end_date
    # get price data from database using sql above
    return excute_sql_to_df(sql)


def slimjab_bidder(start_date, end_date):
    """Generates a bid based on the power and price data from the database."""
    
    power = _get_power_from_db(start_date,end_date).set_index("time")
    price = _get_price_from_db(start_date,end_date).set_index("time")

    df = get_output_template()
    for i in range(len(df)):        # for each row in the output template, so for each 30min interval.
        time = np.datetime64(
            f'{df.loc[i, "applying_date"]} {str(df.loc[i, "hour_ID"] - 1).zfill(2)}'
        )
        if (
            not f"{time}:00:00" in power.index
            or not f"{time}:30:00" in power.index
            or not f"{time}:00:00" in price.index
            or not f"{time}:30:00" in price.index
        ):
            df = df.drop(i)
            continue

        volume = (
            power.loc[f"{time}:00:00", "NetPower"]
            + power.loc[f"{time}:30:00", "NetPower"]
        ) / 2
        estimatedPrice = (
            price.loc[f"{time}:00:00", "price"] + price.loc[f"{time}:30:00", "price"]
        ) / 2
        df.loc[i, "volume"] = abs(volume)
        df.loc[i, "price"] = estimatedPrice
        df.loc[i, "type"] = "BUY" if volume < 0 else "SELL"
    return df
