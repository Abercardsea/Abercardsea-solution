from os import environ
# make a copy of this file and rename it config.py with your own keys
# Details for were we submit bids. Need removing from code at some point.

AIMLAC_RSE_ADDR = '34.67.28.139'                #This might have changed
AIMLAC_RSE_KEY =  #environ.get("AIMLAC_RSE_KEY")

# Other parameters you need to put in your api keys here.
METOFFICE_KEY =
ELEXON_KEY =
BMREPORT_KEY =

DATETIME_FORMAT = "%Y-%m-%dT%H:%MZ"
LATITUDE = 52.1051      #environ.get("LOCATION_LAT")
LONGITUDE = -3.6680     #environ.get("LOCATION_LON")
TIMEZONE = "Europe/London"

# Power generation details.

ALTITUDE = 250.0            # m above sea level
PANEL_TILT = 45.0           # angle panels are tilted at (south facing)
ARRAY_AREA = 50.0 * 50.0    # area covered by array in m^2
BASE_EFFICIENCY = 0.196     # base efficiency of panels
PMPP = -0.0037              # %/C
PMAX_ARRAY = 469_000        # W
