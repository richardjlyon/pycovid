from pycovid import DATA_DIR
from pycovid.data_utils import read_ONS_daily_registrations
import pandas as pd


def test_read_excel():
    """
    GIVEN a filename, rows to skip, columns, and a daterange
    WHEN I get the excel spreadsheet
    THEN verify I get a dataframe with the data
    """
    filename = DATA_DIR / "publishedweek142021.xlsx"
    skiprows = list(range(3)) + list(range(408, 425))
    cols = "A:B"
    daterange = pd.date_range(start="2 Mar 2020", end="9 Apr 2021")

    df = read_ONS_daily_registrations(
        filename=filename, skiprows=skiprows, cols=cols, daterange=daterange
    )

    assert df["UK"].sum() == 150540
