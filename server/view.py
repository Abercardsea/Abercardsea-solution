from flask import Blueprint, render_template, request
from . import db
from sqlalchemy import text
from flask import render_template
from sqlalchemy import text
import pandas as pd
from flask_navigation import Navigation

views = Blueprint('views', __name__)

# we only have one access point. The home route e.g. url will be example.com/
# you could have alternative routes that have different urls e.g. example.com/about


@views.route('/', methods=['GET', 'POST'])
def home():
    '''

    Here we are getting the data from the database and sending it to the frontend server.
    This funciton allso renders the home.html page and sends it to the user.

    return: home.html

    '''
    # get data from the database
    Weather_query = text("""
    SELECT DISTINCT * FROM  met_office
    WHERE DATE(datetime) = (
        SELECT MAX(DATE(datetime)) FROM met_office
    )
    """)

    Windpred_query = text("""
    SELECT DISTINCT *  FROM  windPrediction
    WHERE DATE(time) = (
        SELECT MAX(DATE(time)) FROM windPrediction
    )
    """)

    Solarpred_query = text("""

    SELECT DISTINCT *  FROM  solarPrediction
    WHERE DATE(time) = (
        SELECT MAX(DATE(time)) FROM solarPrediction
    )
    """)

    onsite_query = text("""
    SELECT DISTINCT *  FROM  onsiteEnergy
    WHERE DATE(datetime) = (
        SELECT MAX(DATE(datetime)) FROM onsiteEnergy
    )
    """)

    EnergyUsage_query = text("""
    SELECT *
    FROM elexonB0620
    WHERE "Settlement Date" = (
    SELECT MAX("Settlement Date")
    FROM (
        SELECT DISTINCT "Settlement Date" FROM elexonB0620
    )
    );
    """)

    EnergyType_query = text("""
    SELECT *
    FROM elexonB0620
    WHERE "Settlement Date" = (
    SELECT MAX("Settlement Date")
    FROM (
        SELECT DISTINCT "Settlement Date" FROM elexonB0620
    )
    );
    """)

    Predicted_price_query = text("""

    SELECT DISTINCT *  FROM  pricePrediction
    WHERE DATE(time) = (
        SELECT MAX(DATE(time)) FROM pricePrediction
    )
    """)

    Imbalance_market_query = text("""
    SELECT DISTINCT *  FROM  bmreport
    WHERE DATE(SettlementDateTime) = (
        SELECT DATE(MAX(SettlementDateTime),'-1 day') FROM bmreport
    )
    """)

    try:
        data_wind = pd.DataFrame(db.session.execute(Windpred_query).fetchall())
        data_solar = pd.DataFrame(db.session.execute(Solarpred_query).fetchall())
        data_weather = pd.DataFrame(db.session.execute(Weather_query).fetchall())
        data_onsite_demand = pd.DataFrame(db.session.execute(onsite_query).fetchall())
        data_EnergyUsage_query = pd.DataFrame(db.session.execute(EnergyUsage_query).fetchall()).sort_values(by=['Settlement Period'])
        data_EnergyType_query = pd.DataFrame(db.session.execute(EnergyType_query).fetchall()).sort_values(by=['Settlement Period'])
        data_Predicted_price_query = pd.DataFrame(db.session.execute(Predicted_price_query).fetchall())

        DateTime= data_weather.DateTime.to_list()
        Temperature = data_weather['T'].to_list()
        data_windspeed = data_wind['WindSpeed'].to_list()
        data_windpower = data_wind['WindPower'].to_list()
        data_windDateTime = data_wind['time'].to_list()
        data_solarPower = data_solar['SolarPower'].to_list()
        data_solarDateTime = data_solar['time'].to_list()
        data_EnergyUsage = data_EnergyUsage_query['Quantity'].to_list()
        data_EnergyUsageDateTime = data_EnergyUsage_query['Settlement Date'].to_list()[0]
        data_EnergyUsagePeriods = data_EnergyUsage_query['Settlement Period'].to_list()

        PricePredicted = data_Predicted_price_query['price'].to_list()
        PricePredictedDateTime = data_Predicted_price_query['time'].to_list()

        Imbalance_Market_query = pd.DataFrame(db.session.execute(Imbalance_market_query).fetchall())
        Imbalance_Market = Imbalance_Market_query['ImbalancePriceAmount'].to_list()
        Imbalance_Market_Datetime = Imbalance_Market_query['SettlementDateTime'].to_list()

        status = 1

    except:
        print('error getting db data!! Is the database configured?')
        # all empty lists
        Temperature = []
        DateTime = []
        data_windspeed = []
        data_windpower = []
        data_windDateTime = []
        data_solarPower = []
        data_solarDateTime = []
        data_EnergyUsage = []
        data_EnergyUsageDateTime = []
        data_EnergyUsagePeriods = []
        PricePredicted = []
        PricePredictedDateTime = []
        Imbalance_Market = []
        Imbalance_Market_Datetime = []
        status = 0

    # Date from a DateTime object
    #print(DateTime[0])
    #date = datetime.strptime(DateTime[0],"%Y-%m-%dT%H:%M:%SZ").date()
    #print('DATE: ',date)

    # we are parseing the date from database to the fontend server.

    return render_template("home.html", temps=Temperature, dates=DateTime,
                           windspeed=data_windspeed, windpower=data_windpower,
                           windDateTime=data_windDateTime, solarPower=data_solarPower,
                           solarDateTime=data_solarDateTime, onsite_Datetime=data_onsite_demand['DateTime'].to_list(),
                           onsite_Total_demand=data_onsite_demand['Total demand'].to_list(),EnergyUsage=data_EnergyUsage,
                           EnergyUsageDateTime=data_EnergyUsageDateTime,EnergyUsagePeriods=data_EnergyUsagePeriods,
                           PricePredicted=PricePredicted,PricePredictedDateTime=PricePredictedDateTime,status=status,
                           Imbalance_Market=Imbalance_Market,Imbalance_Market_Datetime=Imbalance_Market_Datetime)

@views.route('/doc', methods=['GET', 'POST'])
def docs():
    return render_template("docs.html")