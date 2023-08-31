import requests
import datetime as dt

clearout_url = '34.67.28.139/auction/market/clearout-prices'


def get_clearout():

    start_date = dt.datetime.now() - dt.timedelta(days=1)
    end_date = dt.datetime.now()+dt.timedelta(days=1)
    host = f"http://{clearout_url}"
    g = requests.get(host, params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()})
    return g

if __name__ == "__main__":
    print(get_clearout())