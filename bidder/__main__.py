import time
import datetime as dt
import numpy as np
from bidder.src.bidding.util import register_bidder, get_output_template, submit_orders, parse_data, get_orders, submit_orders_mock, get_clearout
from bidder.src.bidding.slimjab_bidder import slimjab_bidder
from bidder.src.met_office_api.api import get_met_office_data, save_to_db, get_average_met_office_data, save_to_db_national_average
from bidder.src.elexon_api.elexon_utils import get_bmrs_report, _save_to_database
from bidder.src.onsite.onsite import get_energy_demand, save_to_db_energy
from bidder.src.solar import get_solar_prediction, save_to_db_solar
from bidder.src.wind import get_wind_prediction, save_to_db_wind
from bidder.src.pricing.pricing import predict_price_tomorrow, save_to_db_price
import pandas as pd
import os

def load_environment_variables_from_file(file_path):
    """
    Load environment variables from a text file and add them to the environment.

    Args:
    file_path (str): The path to the text file containing variable assignments.

    Returns:
    None
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Split each line into variable and value (assuming they are separated by '=')
                parts = line.strip().split('=')
                if len(parts) == 2:
                    variable_name, variable_value = parts[0].strip(), parts[1].strip()
                    # Set the environment variable
                    os.environ[variable_name] = variable_value
                else:
                    print(f"Invalid line in the file: {line.strip()}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def aligntime():
    "Compltes when the current time aligns with nearest market period."
    #print("Aligning time...")
    current_minute = dt.datetime.now().minute
    interval = (0,30) # in production (0,30)
    time_aligned = bool(current_minute in interval) # for testing 0,1
    #print(time_aligned, current_minute)
    runtime = 0
    while time_aligned is False:
        time.sleep(1)
        current_minute = dt.datetime.now().minute
        time_aligned = bool(current_minute in interval)
        runtime += 1
        if runtime > 1860:
            raise Exception("Could no align time. Runtime exceeded 31 mins.")



def standard_time(time):
    """Rounds a timestamp to the nearest 30-mins period."""

    date = time.date()
    hour = time.hour
    minute = time.minute
    return f"{date} {hour:02}:{(minute//30)*30:02}"



def main():

    '''Autobidder main functions here!!'''

    tformat = '%Y-%m-%dT%H:%MZ'

    print("AUTOBIDDER loop Started!")

    #aligntime()     # inital wait for time alignment.
    # get data from api's and save to database B0612 & B1620 yesterday data.
    # infinite loop so the function will operate indefinetly.
    # B0620-predicted usage tomorrow, B1620 Actuall usage by type. elexon generation data
    dates = [(dt.datetime.now()-dt.timedelta(days=1)).strftime('%Y-%m-%d'),
                    (dt.datetime.now()-dt.timedelta(days=2)).strftime('%Y-%m-%d')] # otherwise it will not properly populate.

    responce = get_bmrs_report('B0620', dates[0], '*')
    _save_to_database(responce, 'B0620')

    responce = get_bmrs_report('B1620', dates[1], '*')
    _save_to_database(responce, 'B1620')
    while True:

        timestap = standard_time(dt.datetime.now())

        if int(time.strftime("%H")) == 9  and int(time.strftime("%M")) > 5:         # Submit all day bids between 7:00 and 7:05. buffer to account for gitter.
            print("Starting to generate bids..., time: ", timestap)
            print("Getting energy generation data...")

            # get metoffice data get next day forcast 11pm-11pm.
            met_data = get_met_office_data()
            save_to_db(met_data)
            print('!!!!! GETTING AVERAGE MET DATA !!!!!')
            met_ave_data = get_average_met_office_data()
            save_to_db_national_average(met_ave_data)
            print('met ave Data ', met_ave_data)

            # B0620-predicted usage tomorrow, B1620 Actuall usage by type. elexon generation data
            dates = [(dt.datetime.now()+dt.timedelta(days=1)).strftime('%Y-%m-%d'),
                            (dt.datetime.now()-dt.timedelta(days=1)).strftime('%Y-%m-%d')] # otherwise it will not properly populate.

            responce = get_bmrs_report('B0620', dates[1], '*')
            _save_to_database(responce, 'B0620')

            responce = get_bmrs_report('B1620', dates[1], '*')
            _save_to_database(responce, 'B1620')

            #call api to get energy demand from datacenter data and save to database.

            energy_data = get_energy_demand(forecast=met_data) # get onsite energy data
            save_to_db_energy(energy_data)
            energy_demand = energy_data['Total demand'].to_numpy()

            # get solar and wind data
            solar = get_solar_prediction(met_data)
            save_to_db_solar(solar)
            solar_power = solar['SolarPower'].to_numpy()
            print('Solar',solar_power)
            wind = get_wind_prediction(met_data)
            save_to_db_wind(wind)
            wind_power = wind['WindPower'].to_numpy()
            print('Wind',wind_power)

            # get price data
            price = predict_price_tomorrow()
            price = price.reset_index()
            price.rename(columns={'index':'time'}, inplace=True)
            save_to_db_price(price)
            price_list = price['price'].to_numpy()

            date = (dt.datetime.now()+dt.timedelta(days=1)).strftime('%Y-%m-%d')
            # create array of 48 dates
            date = [date]*48
            period = np.arange(1,49,1)
            sys_price = price_list
            net_generation = solar_power + wind_power - energy_demand
            orders = get_orders(date,period,net_generation,sys_price)

            # submit orders
            orders = pd.DataFrame(orders)
            print("Submitting orders...")
            try:
               # responce = submit_orders(orders)
                #responce = submit_orders(orders)
                print("Sever Reponded with: ",responce.status_code)
            except:
                print("Failed to submit orders... Continuing.")


        # wait for next 30-min period
        print("Waiting for next 30-min period...")

        for i in range(26):     # wait for 26-mins
            time.sleep(60)      # wait for 1-min

        aligntime()

def _development__():
    """Development function to test functions."""
    print("Starting Autobidder...")
    print("----------------------------------")
    print("Getting Met Office data...")
    print("----------------------------------")
    # gets metoffice data get newxt day forcast 11pm-11pm.
    met_data = get_met_office_data()
    #save_to_db(met_data)
    #print("Getting Elexon data...")
    print("----------------------------------")
    print("Getting Elexon data...")
    print("----------------------------------")
    # B0620-predicted usage tomorrow, B1620 Actuall usage by type. elexon generation data
    #date = '2023-05-07'
    #codes = ['B0620','B1620']
    #for code in codes:
    #    responce = get_bmrs_report(code, date, '*')
    #    _save_to_database(responce, code)

    #print("Calculating onsite energy data...")

    # get onsite energy data
    print("----------------------------------")
    print("Calculating onsite energy data...")
    print("----------------------------------")
    energy_data = get_energy_demand(forecast=met_data)
    energy_demand = energy_data['Total demand'].to_numpy()
    print(energy_data)

    # solar
    print("----------------------------------")
    print("Calculating solar energy data...")
    print("----------------------------------")
    solar = get_solar_prediction(met_data)
    print(solar)
    solar_power = solar['SolarPower'].to_numpy()
    # wind
    print("----------------------------------")
    print("Calculating wind energy data...")
    print("----------------------------------")
    wind = get_wind_prediction(met_data)
    print(wind)
    wind_power = wind['WindPower'].to_numpy()

    print("----------------------------------")
    print("Get CO2 data...(ignore since, isnt being used to predict.)")
    print("----------------------------------")

    # get co2 data
    print("----------------------------------")
    print(" Predict prices based on forcasted enegry generation...")
    print("----------------------------------")

    price = predict_price_tomorrow()
    # set price type to datatime
    price = price.reset_index()
    price.rename(columns={'index':'time'}, inplace=True)
    save_to_db_price(price)
    price_list = price['price'].to_numpy()


    date = dt.datetime.now().strftime('%Y-%m-%d')

    # get market orders (price predictions)
    # submit orders

    # get order in correct format.
    date = (dt.datetime.now()+dt.timedelta(days=1)).strftime('%Y-%m-%d')
    # create array of 12 dates
    date = [date]*48
    period = np.arange(1,49,1)
    sys_price = price_list
    print(sys_price)
    net_generation = solar_power + wind_power - energy_demand
    #print(net_generation)
    orders = get_orders(date,period,net_generation,sys_price)
    print(orders)
    orders_asframe = pd.DataFrame(orders)
    print(orders_asframe)
    #parse_data = parse_data(data=orders)


    #submit_orders(orders)

def test_clearout():
    """Test function to get clearout prices. Currently Not Happening."""
    clearout = get_clearout()
    print(clearout)


# initiate when not imported by called from command line.
if __name__=="__main__":
    #test_clearout()
    main()
    #_development__()


