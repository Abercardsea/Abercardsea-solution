import json
from datetime import date, datetime, timedelta
import datetime as dt
import pandas as pd
import requests
from flask import g
from sqlalchemy import create_engine
import bidder.src.config as config
import numpy as np

BIDDERS = {}


def check_outputs(frame):
    """check frame contains these columns:
    hour_ID, applying_date, volume, price, type
    """
    assert isinstance(frame, pd.DataFrame), f"expect pd.Dataframe, got: {type(frame)}"
    for col in ["hour_ID", "applying_date", "volume", "price", "type"]:
        assert col in frame.columns, f"missing column: {col}"


def parse_data(data, table='pricePrediction'):
    """query the database for data to feed into the bidder function"""
    assert isinstance(data, dict), f"expect a `dict`, got: {type(data)}"
    parsed_data = {}
    engine = create_engine(f"sqlite:///database/llanwrydd.db")
    for key, query in data.items():
        parsed_data[key] = pd.read_sql(query.format(table), engine)
    return parsed_data


def register_bidder(name, *, args={}, data=None, default=False):
    
    """function wrapper to register and pre-process the bidder functions"""

    def wrapper(fn):
        def bidder_function(**kwargs):
            """bidding procedure:
            1. query database for data
            2. run defined function
            3. place bids via RSE API
            """
            parsed_data = parse_data(data, args)
            outputs = fn(**parsed_data, **args, **kwargs)
            check_outputs(outputs)
            resp = place_orders(outputs)
            return resp

        # register bidder function
        BIDDERS[name] = bidder_function
        if default:
            assert "default" not in BIDDERS, "duplicated `default`"
            BIDDERS["default"] = bidder_function
        return fn

    return wrapper


# make predictions 2 days ahead so that the bids are accepted
def get_output_template(dt: date = date.today() + timedelta(days=1)):
    """Create an empty output DataFrame with following columns:

    hour_ID: int (1-24)
    applying_date: str, (YYYY-MM-DD)
    volume: float
    price: float
    type: str (BUY or SELL)

    the time range is 24-H from 9AM of given date to the next morning at 8AM
    """
    cols = ["hour_ID", "applying_date", "volume", "price", "type"]
    # create template
    data = [(hour, dt, 0.0, 0.0, "BUY") for hour in range(1, 25)]
    df = pd.DataFrame(data=data, columns=cols)
    df["applying_date"] = df["applying_date"].map(lambda d: d.isoformat())
    return df


def submit_orders_mock(orders: pd.DataFrame) -> bool:
    """set bids via RSE API"""
    mock_url = 'https://37ce7e0f-dafd-454c-81d8-6576415f7741.mock.pstmn.io/aimlac'
    #url = #f"http://{config.AIMLAC_RSE_ADDR}/auction/bidding/set"
    #key = config.AIMLAC_RSE_KEY
    orders = json.loads(orders.to_json(orient="records"))

    #resp = requests.post(url, json=dict(key=key, orders=orders))
    mock_resp = requests.post(mock_url, json=dict(orders=orders))
    return mock_resp


def submit_orders(orders: pd.DataFrame) -> bool:
    """set bids via RSE API"""
    url = f"http://{config.AIMLAC_RSE_ADDR}/auction/bidding/set"
    key = config.AIMLAC_RSE_KEY
    orders = json.loads(orders.to_json(orient="records"))
    resp = requests.post(url, json=dict(key=key, orders=orders))
    return resp

def get_clearout():
    """Fetches previous day's clearout prices. Not working."""

    start_date = dt.date.today() - dt.timedelta(days=1)
    end_date = dt.date.today() + dt.timedelta(days=1)
    
    AIMLAC_CC_MACHINE = "34.67.28.139"
    assert AIMLAC_CC_MACHINE is not None
    host = f"http://{AIMLAC_CC_MACHINE}"

    g = requests.get(url=host + f"/auction/market/clearout-prices",
                     params=dict(start_date=start_date.isoformat(),
                                 end_date=end_date.isoformat()))

    # Some data should be present!
    #assert len(g.json()) > 0

    return g.status_code


def get_orders( date, period, net_generation, sys_price):
    """Calculates bid quantity and bid direction and returns resulting market
       order.

    Args:
        date (list,str)             : Date or list of dates for the market bid.
        period (list,int)           : Period or list of periods for the market
                                      bid.
        net_generation (list,float) : Predicted net generation in KWh.
        sys_price (list,float)      : Predicted market (system) price in
                                      GBP/MWh.

    Returns:
        orders (list(dict),dict) : Dict or list of dicts containing market bids.
    """

    assert isinstance(date, (list, str, np.ndarray))
    assert isinstance(period, (list, int, np.ndarray))
    assert isinstance(net_generation, (list, float, np.ndarray))
    assert isinstance(sys_price, (list, float, np.ndarray))

    # Check for single market bid
    #if not all(
    #    isinstance(v, (list, np.ndarray))
     #   for v in [date, period, net_generation, sys_price]
    #):
    #    direction = "SELL" if net_generation >= 0 else "BUY"

    #    if direction == "BUY":
    #        sys_price = 150  # Buy at National Grid rate of 15p/kWh

    #    orders = {
    #        "applying_date": date,
    #        "hour_ID": period,
    #        "type": direction,
    #        "volume": round(abs(net_generation) / 1000, 3),  # Convert to MWh
    #        "price": round(sys_price, 2),
    #    }
    #else:
    orders = []
    for pos, _ in enumerate(date):

        direction = "SELL" if net_generation[pos] >= 0 else "BUY"

        if direction == "BUY":
            sys_price[pos] = 150  # Buy at National Grid rate of 15p/kWh

        order = {
            "applying_date": date[pos],
            "hour_ID": int(period[pos]),
            "type": direction,
            "volume": round(abs(net_generation[pos]) / 1000, 4),  # Convert to MWh
            "price": round(sys_price[pos], 2),
        }
        orders.append(order)

    return orders