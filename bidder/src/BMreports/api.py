import requests
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import pandas as pd
import csv
import xml.etree.ElementTree as ET
import bidder.src.config as config
from io import StringIO


service_type = 'csv'
API_key = config.BMREPORT_KEY


def get_bmreport_data_imbalance():
    """Get the BMRS data for a given date.
    """
    base_url = 'https://api.bmreports.com/BMRS/B1770/V1'
    date = datetime.today()
    formatted_date = date.strftime("%Y-%m-%d")
    minusOne = date - timedelta(days=1)
    formatted_minus = minusOne.strftime("%Y-%m-%d")
    url = f"{base_url}?APIKey={API_key}&SettlementDate={formatted_minus}&Period=*&ServiceType={service_type}"
    response = requests.get(url)
    csv_data = response.text
    # drop the first 5 lines
    csv_data = csv_data.split("\n", 4)[-1]
    csv_file = StringIO(csv_data)
    df = pd.read_csv(csv_file, sep=",",header=0)
    # drop all columns except the ones we want
    df = df[['ImbalancePriceAmount', 'SettlementDate', 'SettlementPeriod']]
    # drop duplicate rows
    df = df.drop_duplicates()
    # reset the index
    df = df.reset_index(drop=True)
    # drop nana
    df = df.dropna()
    df['SettlementPeriod'] = df['SettlementPeriod'] * 30
    # convert the date and period to a datetime
    df['SettlementDate'] = pd.to_datetime(df['SettlementDate'])
    # turn settlement period into a timedelta
    df['SettlementPeriod'] = pd.to_timedelta(df['SettlementPeriod'], unit='m')
    # add
    df['SettlementDateTime'] = df['SettlementDate'] + df['SettlementPeriod']
    # drop the settlement date and period
    df = df.drop(columns=['SettlementDate', 'SettlementPeriod'])

    return df

def write_to_db(df):

    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    df.to_sql('bmreport', engine, if_exists='append', index=False)


def get_bmreport_data_dayaheadmarket():
    base_url = "https://api.bmreports.com/BMRS/MID/V1"
    date = datetime.today()
    formatted_date = date.strftime("%Y-%m-%d")
    minusOne = date - timedelta(days=1)
    formatted_minus = minusOne.strftime("%Y-%m-%d")
    url = f"{base_url}?APIKey={API_key}&SettlementDate={formatted_minus}&Period=*&ServiceType={service_type}"

    response = requests.get(url)
    csv_data = response.text
    # drop the first 5 lines

    csv_data = csv_data.split("\n", 1)[-1]
    csv_file = StringIO(csv_data)
    df = pd.read_csv(csv_file, sep=",",header=None)
    df.rename(columns={1: 'Data',2: 'Date', 3: 'Period',4:'Price',5:'Quanity'}, inplace=True)
    df = df[['Price', 'Date', 'Period','Quanity']]
    # date and time to datetime

    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df['Period'] = df['Period'] * 30
    df['Period'] = pd.to_timedelta(df['Period'], unit='m')
    df['DateTime'] = df['Date'] + df['Period']
    df = df.drop(columns=['Date', 'Period'])

    return df


def save_dayaheadmarket_to_db(df):
    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    df.to_sql('bmreport_dayaheadmarket', engine, if_exists='append', index=False)


if __name__ == '__main__':
    #write_to_db(get_bmreport_data_imbalance())
   save_dayaheadmarket_to_db(get_bmreport_data_dayaheadmarket())