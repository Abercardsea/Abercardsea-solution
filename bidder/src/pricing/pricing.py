# -*- coding: utf-8 -*-
"""Functions to collect energy market data from Elexon.

Adapted from author: jadot-bp
Author: Rhys Shaw (team ABERCARDSEA).

"""

import datetime as dt
import pickle
from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.sql import text
import numpy as np
import pandas as pd

# need this to unpack the pickles
import sklearn
from flask import g

m_model_p = None

# Load autobidder ML model
with open("bidder/src/pricing/model.p", "rb") as handle:
    m_model_p = pickle.load(handle)

m_scalar_p = None
# Load data scaler for autobidder
with open("bidder/src/pricing/scaler.p", "rb") as handle:
    m_scalar_p = pickle.load(handle)


def prepare_data_frame(
    b0620_data: pd.DataFrame, b1620_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Adapted from `get_forecast(date, period)` in the slimjab repository

    I think the data and period for both the frames has to be identical for the model later
    down the line to work.

    Returns:
        forecast (pd.DataFrame) : pd.DataFrame containing market forecast
                                  according to model pattern.
    """
    print("IN PERAPRE DATA FRAME")
    print(b1620_data.info())
    print(b0620_data.info())
    output = pd.merge(b1620_data, b0620_data, on=["settlementDate", "settlementPeriod"])
    print(output.info())
    output.loc[:, "settlementDate"] = pd.to_datetime(output["settlementDate"])
    output.loc[:, "settlementDate"] -= dt.datetime(1970, 1, 1)  # Since epoch 1st January 1970
    output.loc[:, "settlementDate"] = output.loc[:, "settlementDate"].dt.days # Convert to days since epoch.
    print(output["settlementDate"])
    # Pattern dictates current feature arrangement for autobidder model

    pattern = [
        "settlementDate",
        "settlementPeriod",
        "biomass",
        "hydroPumpedStorage",
        "hydroRunofriverAndPoundage",
        "fossilHardCoal",
        "fossilGas",
        "fossilOil",
        "nuclear",
        "other",
        "quantity",
        "solar",
        "windOffshore",
        "windOnshore"
    ]

    return output[pattern]


def get_price_estimate(forecast) -> Tuple[str, int, float]:
    """Calculates the estimated market sell price for the given date and
       period.

    Returns:
        (str, int, float) tuple representing the forecast date, market period
        and predicted market price.
    """
    global m_scalar_p, m_model_p

    # apparently:
    # > Maximum time delta supported by ML model
    # so we'll need a check to see if the time-difference
    # of the models is
    #
    #   delta = (date - dt.datetime.now()).days * 48 + period
    #   delta > 2 * 48
    #
    # so a 24 hour = 48 * 30 minute period ?
    #
    #  if (delta > 2*48):
    #      price = 'NaN'
    #  else:

    rescaled = m_scalar_p.transform(forecast.values[:])
    price = m_model_p.predict(rescaled)[0]
    return price


def get_price_forecast(forecast) -> list:
    """Generates the Day-Ahead (11pm-11pm) market price forecast.

    Returns:
        np.ndarray : Array of market prices.
    """

    dates = set(forecast["settlementDate"])
    #print(dates)
    outputs = {}
    #print(forecast)
    # change type of settlementDate to period, so that it can filter.
    forecast["settlementPeriod"] = forecast["settlementPeriod"].astype(int)
    for date in dates:

        prices = []
        for i in range(1, 49):
            #print(date,i)
            selection = forecast[forecast['settlementDate'] == date]
            #print(selection.info())
            selection = selection[selection['settlementPeriod'] == i]
            #print(selection.info())
            if not selection.empty:
                estimate = get_price_estimate(selection)
                prices.append(estimate)
            else:
                prices.append(float("nan"))

        outputs[date] = prices

    return pd.DataFrame(outputs)


def predict_price_tomorrow():
    engine = create_engine("sqlite:///database/llanwrydd.db")
    conn = engine.connect()
    today = dt.date.today()
    tomorrow = today + dt.timedelta(days=1)
    yesterday = today - dt.timedelta(days=1)
    formatted_yesterday = yesterday.strftime("%Y-%m-%d")
    formatted_tomorrow = tomorrow.strftime("%Y-%m-%d")
    # Construct the SQL query with proper formatting
    query = text("SELECT * FROM elexonB0620 WHERE \"Settlement Date\" = '"+formatted_yesterday+"';")

    # Execute the query and fetch the data into a DataFrame
    elexonB0620 = pd.read_sql_query(query, conn)

    query = text("SELECT * FROM elexonB1620 WHERE \"Settlement Date\" = '"+formatted_yesterday+"';")
    elexonB1620 = pd.read_sql_query(
        query,
        conn,
    )
    # change column names to match the model
    elexonB0620 = elexonB0620.rename(
        columns={
            "Settlement Date": "settlementDate",
            "Settlement Period": "settlementPeriod",
            "Quantity": "quantity",
        }
    )
    print(elexonB0620.info())
    print(elexonB1620.info())
    elexonB1620 = elexonB1620.rename(
        columns={
            "Settlement Date": "settlementDate",
            "Settlement Period": "settlementPeriod",
            "Power System Resource Type": "type",
            "Quantity": "quantity",
            "Biomass": "biomass",
            "Hydro Pumped Storage": "hydroPumpedStorage",
            "Hydro Run-of-river and poundage": "hydroRunofriverAndPoundage",
            "Fossil Hard coal": "fossilHardCoal",
            "Fossil Gas": "fossilGas",
            "Fossil Oil": "fossilOil",
            "Nuclear": "nuclear",
            "Other": "other",
            "Solar": "solar",
            "Wind Offshore": "windOffshore",
            "Wind Onshore": "windOnshore",
        }
    )
    forecast = prepare_data_frame(elexonB0620, elexonB1620)
    print(forecast)
    forecast.settlementDate += 2
    #print(forecast['settlementDate'])
    forecast = get_price_forecast(forecast)
    print(forecast)
    series = pd.Series(
        data=np.round(forecast.values.ravel(), 2),
        index=pd.to_datetime(
            [f"{tomorrow} {i//2:02d}:{(i%2)*30:02d}:00" for i in range(48)]
        ),
        name="price",
    ).dropna()
    return series.to_frame()

def append_unique_data_to_database(new_data, table_name, connection_string):
    # Create a SQLAlchemy engine to connect to the database
    engine = create_engine(connection_string,echo=True)
    
    # Retrieve existing data from the database table
    query = text("SELECT * FROM "+table_name)
    with engine.connect() as conn:
        result = conn.execute(query)
        existing_data = pd.DataFrame(result.fetchall(), columns=result.keys())
    
    # Compare the new data with the existing data to identify duplicates
    duplicate_rows = pd.merge(existing_data, new_data, how='inner')
    
    # Filter out the duplicates from the new data
    filtered_new_data = new_data[~new_data.index.isin(duplicate_rows.index)]
    
    # Append the filtered new data to the existing data in the database
    filtered_new_data.to_sql(table_name, engine, if_exists='append', index=False)

def save_to_db_price(predicted_prices):
    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    predicted_prices.to_sql('pricePrediction', engine, if_exists='replace', index=False)
    #append_unique_data_to_database(predicted_prices, 'pricePrediction', "sqlite:///database/llanwrydd.db")
    print("saved to database")