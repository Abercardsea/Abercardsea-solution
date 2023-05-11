import json

import pandas
import pytest

from bidder.test.samples.sample_data import sample_time_series


@pytest.fixture(scope="session")
def timeseries() -> pandas.DataFrame:
    yield sample_time_series
