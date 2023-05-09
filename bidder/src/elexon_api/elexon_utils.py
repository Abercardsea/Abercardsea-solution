import numpy as np
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from typing import Union, List, Optional

ELEXON_KEY = '8t20g6yokupgit5'
user_guide = 'https://bscdocs.elexon.co.uk/guidance-notes/bmrs-api-and-data-push-user-guide'
CODE_DESCRIPTORS = {
    "B1720": "Amount of balancing reserves under contract",
    "B1730": "Prices of procured balancing reserves",
    "B1740": "Accepted aggregated offers",
    "B1750": "Activated balancing energy",
    "B1760": "Prices of activated balancing energy",
    "B1770": "Imbalance prices",  # This is the one we want to integrate imbalance.
    "B1780": "Aggregated imbalance volumes",
    "B1810": ("CrossBorder balancing volumes of exchanged bids" " and offers"),
    "B1820": "CrossBorder balancing prices",
    "B1830": "CrossBorder balancing energy activated",
    "B0610": "Actual total load per bidding zone",
    "B0620": "Day ahead total load forecast per bidding zone",
    "B1430": "Day ahead aggregated generation",
    "B1440": "Generation forecasts for wind and solar",
    "B1610": "Actual generation output per generation unit",
    "B1620": "Actual aggregated generation perType",
    "B1630": ("Actual or estimated wind and solar power" " generation"),
    "B1320": "Congestion management measure counter-trading",
}

# we want elexonB0620 and elexonB1620
# elexonB0620 is the day ahead load forecast
# elexonB1620 is the actual aggregated generation per type


def get_bmrs_report(code: str, date: str, period: int) -> pd.DataFrame:
    APIKEY = ELEXON_KEY
    date = date
    period = period
    code = code
    url = (
        f"https://api.bmreports.com/BMRS/{code}/v1?APIKey={APIKEY}"
        f"&SettlementDate={date}&Period={period}&ServiceType=csv"
    )
    reponce = requests.get(url)
    return _response_to_df(reponce.content.decode("utf-8"))


def _response_to_df(response_string: str) -> pd.DataFrame:
    """Converts utf-8 decoded response string to a pandas.DataFrame object.

    Args:
        response_string (str) : utf-8 decoded string from response content

    Returns:
        pandas.DataFrame object
    """
    assert len(response_string) != 0

    # Unpack csv formatted response_string
    data_string = response_string.split("\n")
    header = data_string[4].split(",")
    header[0] = header[0].lstrip("*")  # Catch leading asterisk
    content = [x.split(",") for x in data_string[5:-1]]

    return pd.DataFrame(content, columns=header)

def _save_to_database(elexon_data,code):
    if code =='B0620':
        processed_data = elexon_data[['Settlement Date', 'Settlement Period', 'Quantity', 'Active Flag']]
    elif code=='B1620':
        Anchors = ['Settlement Date', 'Settlement Period']
        label = 'Power System Resource  Type'
        target = 'Quantity'
        processed_data = df_unstacker(elexon_data, Anchors, label, target)
        
    
    engine = create_engine("sqlite:///database/llanwrydd.db", echo=True)
    processed_data.to_sql(f'elexon{code}', engine, if_exists='append', index=False)
    #append_unique_data_to_database(processed_data, f'elexon{code}', "sqlite:///database/llanwrydd.db")
    print("saved to database")


def drop_non_unique(
    dataframe: pd.DataFrame, keep_cols: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """Drop non-unique columns.

    Drops columns with non-unique entries and returns a new pandas.DataFrame
    object.

    Args:
        dataframe (pd.DataFrame) : pandas.DataFrame object
        keep_cols (str,list)     : string or list of strings corresponding to
                                   the column headers that are to be kept.

    Returns:
        pandas.DataFrame object
    """
    assert isinstance(dataframe, pd.DataFrame)

    new_dataframe = dataframe.copy()
    for cname in new_dataframe.columns.values:
        if keep_cols is None or cname in keep_cols:
            pass
        elif len(new_dataframe[cname].unique()) == 1:
            new_dataframe = new_dataframe.drop(columns=cname)

    return new_dataframe




def df_unstacker(
    data: pd.DataFrame,
    anchor_column: Union[str, list],
    label_column: str,
    target_column: str,
) -> pd.DataFrame:
    """Unstack a stacked dataframe.

    Unstacks a target column of a pandas.DataFrame object with respect to a
    specified anchor column(s), returning a new pandas.DataFrame with the
    target column relabelled according to the label column.

    Args:
        data (pd.DataFrame)              : pandas.DataFrame object containing a
                                           stacked column
        anchor_column (Union[str, list]) : Name or list of names of columns which
                                           will be anchored during unstacking
        label_column (str)               : Name of column which will be used to
                                           re-label the target column
        target_column (str)              : Name of column which is to be unstacked
    Returns:
        pd.DataFrame: unstacked data
    """
    assert isinstance(data, pd.DataFrame)
    assert isinstance(anchor_column, (str, list))
    assert isinstance(label_column, str)
    assert isinstance(target_column, str)

    # Generate temporary dataframe to collect unique anchor values
    temp_df = data[anchor_column].drop_duplicates()

    unique_values = []
    for anchor_label in anchor_column:
        unique_values.append(temp_df[anchor_label].values[:])

    out_df = pd.DataFrame()  # Prepare empty dataframe for concatenation

    # Iterate through possible unique pairs of anchor values
    for pos, unique_pair in enumerate(list(zip(*unique_values))):

        mask = 0  # Create mask to slice out anchored values
        for label_pos, anchor_label in enumerate(anchor_column):
            mask += (data[anchor_label] == unique_pair[label_pos]).values[:]
        mask = mask // len(anchor_column)  # Integer division gets boolean mask

        temp_df = drop_non_unique(data[mask.astype(bool)], target_column)
        temp_df = temp_df[[label_column, target_column]]

        headers = [i.strip('"') for i in temp_df[label_column].unique()]
        quantities = list(temp_df[target_column])

        # Add anchor names and values to headers and quantities
        headers = list(anchor_column) + headers
        quantities = list(unique_pair) + quantities

        # Construct new unstacked dataframe
        unstacked_df = pd.DataFrame(
            np.asarray(quantities).reshape(1, -1), columns=headers, index=[pos]
        )

        # Concatenate with output dataframe
        out_df = pd.concat((out_df, unstacked_df), axis=0, ignore_index=True)

    return out_df


