import requests
from bidder.src.met_office_api.met_office_utils import interp_30min, cut_frame
from sqlalchemy import create_engine
import bidder.src.config as config

met_office_key = config.METOFFICE_KEY
symbol_meaning = [
'Wind direction (16 point compass)',
'Wind speed (mph)',
'Screen temperature (degrees Celsius)',
'Weather Type (Definitions of codes)',
'Visibility (Definitions of codes)',
'Screen relative humidity (%)',
'Wind gust (mph)',
'Feels like temperature (degrees Celsius)',
'UV Index (Definitions of codes)',
'Precipitation Probability (%)'
]
def interpolate_api_responce(responce):
    return cut_frame(interp_30min(responce))


def get_met_office_data():
    base_met_office_url = 'http://datapoint.metoffice.gov.uk/public/data/'
    resource = 'val/wxfcs/all/json/3507' # this gets the hourly 24hr forcast for that day.
    url = base_met_office_url + resource

    responce = requests.get(url, params={'key': met_office_key, 'res': '3hourly'})
    assert responce.status_code == 200
    return interpolate_api_responce(responce)

def get_average_met_office_data():
    '''Gets the national average forcast'''
    base_met_office_url = 'http://datapoint.metoffice.gov.uk/public/data/'
    resource = 'val/wxfcs/regionalforecast/json/515' # uk averge forcast
    url = base_met_office_url + resource

    responce = requests.get(url, params={'key': met_office_key,'res': '3hourly'})

    assert responce.status_code == 200
    return interpolate_api_responce(responce)


def save_to_db(processed_data):
    # works
    #processed_data = get_met_office_data()
    # save to db
    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    processed_data.to_sql('met_office', engine, if_exists='append', index=False)



def save_to_db_national_average(processed_data):
    # works
    #processed_data = get_met_office_data()
    # save to db
    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    processed_data.to_sql('met_office_ave', engine, if_exists='append', index=False)


if __name__ == '__main__':
    responce = get_average_met_office_data()
    # save text respoce to markdown file
    #with open('met_office_api.md', 'w') as f:
    #    f.write(responce.text)
    print(responce.text)

    #respnce = save_to_db()
    #print(responce)
