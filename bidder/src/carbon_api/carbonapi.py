import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine

base_url = "https://api.carbonintensity.org.uk/intensity/date/"

def get_carbon_intensity(date):
    """
    Get carbon intensity data from the Carbon Intensity API.
         This will get the pervoius days carbon intensity data.

    Args:
        (datetime): Current date.

    Returns:
        pandas.DataFrame: Date | Actual | Index

    """

    url = f"{base_url}{date.strftime('%Y-%m-%d')}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data['data'])
    #df['forecast'] = df['intensity'].apply(lambda x: x['forecast'])
    df['actual'] = df['intensity'].apply(lambda x: x['actual'])
    df['index'] = df['intensity'].apply(lambda x: x['index'])
    # drop intensity column
    df.drop(columns={'intensity','to'}, axis=1, inplace=True)
    # rename from to datetime
    df.rename(columns={'from': 'time','actual':'intensity','index':'ind'},inplace=True)

    return df

def save_carbon_intensity_to_database(df):
    # works
    #processed_data = get_met_office_data()
    # save to db

    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    df.to_sql('carbonIntensity', engine, if_exists='append', index=False)


def test_get_carbon_intensity():
    # todays date
    today = datetime.now() - timedelta(days=2)
    # get carbon intensity data for today
    df = get_carbon_intensity(today)
    print(df)


if __name__ == "__main__":
    # used to test the api call.
    today = datetime.now() - timedelta(days=2)
    df = get_carbon_intensity(today)
    # save to database
    save_carbon_intensity_to_database(df)
