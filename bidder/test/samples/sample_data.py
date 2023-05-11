import pandas as pd

# read metoffice fake data
series = pd.read_csv('bidder/test/samples/met_office.csv')

def sample_time_series():
    return series