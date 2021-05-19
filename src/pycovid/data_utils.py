"""
data_utils.py

Utilities for preparing data for COVID-19 analysis.
"""


from typing import Tuple

import numpy as np
import pandas as pd
from pycovid import DATA_DIR


def read_daily_registrations(workbook, skiprows, cols, daterange) -> pd.DataFrame:
    """Read raw ONS data for daily deaths where COVID-19 is mentioned on the certificate."""
    df = pd.read_excel(
        workbook,
        sheet_name="Covid-19 - Daily registrations",
        usecols=cols,
        skiprows=skiprows,
    )

    # ONS date formatting is screwed: replace with generated dates
    df["Date"] = daterange
    df.set_index("Date", inplace=True)

    return df


def read_vaccination_data(workbook: str) -> pd.DataFrame:
    """Read NHS Vaccination data for England and return as a dataframe."""
    skiprows = list(range(12)) + list(range(100, 500))
    df = pd.read_excel(
        DATA_DIR / workbook,
        sheet_name="Vaccination Date",
        usecols="B,T",
        skiprows=skiprows,
        parse_dates=True,
        index_col=0,
    )
    df.columns = ["Total doses"]

    return df


def prepare_owid_data(csvfile: str) -> pd.DataFrame:
    """Extract Our World In Data data and return as a dataframe."""

    filename = DATA_DIR / csvfile
    df_raw = pd.read_csv(
        filename,
        index_col="date",
        parse_dates=True,
        usecols=["date", "location", "new_deaths_smoothed_per_million"],
    )
    df_uk = df_raw[df_raw["location"].str.contains("United Kingdom")]
    df_india = df_raw[df_raw["location"].str.contains("India")]

    df = pd.DataFrame(
        pd.concat(
            [
                df_uk["new_deaths_smoothed_per_million"],
                df_india["new_deaths_smoothed_per_million"],
            ],
            axis=1,
        )
    )
    df.columns = ["UK", "India"]
    return df


def prepare_fatal_infection_data(
    workbook: str, region: str = "UK", start_date: str = None, end_date: str = None
) -> pd.DataFrame:
    """
    Construct a timeseries dataframe of fatal infections.

    Fatal infection rate is computed by timeshifting COVID-19 registered fatalities. Fatalities are not recorded at
    weekends, so we smooth the raw data with a rolling window.

    :param region: UK region ('England and Wales', etc.), defaults to "UK"
    :param start_date: Start date e.g. "1 Mar 2020", defaults to start of data set
    :param end_date: End date e.g. "1 Apr 2021", defaults to last of data set
    :return: a dataframe of smoothed fatal infection rate and log fatal infection rate
    """

    INFECTION_TO_DEATH_DAYS = 28

    # get the raw death data #####################################################

    filename = DATA_DIR / workbook
    skiprows = list(range(3)) + list(range(408, 425))
    cols = "A:P"
    daterange = pd.date_range(start="2 Mar 2020", end="9 Apr 2021")

    df = read_daily_registrations(
        workbook=filename, skiprows=skiprows, cols=cols, daterange=daterange
    )
    total_deaths = df[region].sum()

    start_date, end_date = make_dates(df, start_date, end_date)

    # compute fatal infection from death #########################################

    # extend dates to allow deaths to be shifted forward by INFECTION_TO_DEATH_DAYS
    idx = pd.date_range(
        df.index[0] - pd.Timedelta(days=INFECTION_TO_DEATH_DAYS), df.index[-1]
    )
    df = df.reindex(idx)

    # compute fatal infections
    infections = df[region].shift(periods=-INFECTION_TO_DEATH_DAYS)

    # smooth: this discards a small number of infections, so scale back up
    infections_smoothed = infections.rolling(window=7, center=True).mean()
    correction_factor = infections.sum() / infections_smoothed.sum()
    infections_smoothed *= correction_factor
    assert abs(infections_smoothed.sum() / total_deaths) > 0.9999999

    # log
    infections_log = np.log10(infections_smoothed)

    # construct dataframe
    data = {
        "deaths (raw)": df[region],
        "infections": infections_smoothed,
        "infections (log)": infections_log,
    }
    df = pd.concat(data, axis=1)
    df = df.loc[(df.index >= start_date) & (df.index <= end_date)]

    return df


def polyfit(
    df: pd.Series, start_date: str, end_date: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute the polynomial fit for df between start_date and end_date.

    :param df: The data to polyfit
    :param start_date: The date of the start of the interpolation
    :param end_date: The date of the end of the interpolation
    :return: a tuple containing the fits for log(infection) and infection
    """

    # reduce time range
    df = df.loc[start_date:end_date]

    # compute model and predictor
    X = pd.Series(range(1, len(df) + 1), index=df.index)
    model = np.polyfit(X, df, 1)
    predict = np.poly1d(model)

    idx = pd.date_range(start=start_date, end=end_date)

    log_infections_fit = pd.DataFrame(predict(X), index=idx)
    infections_fit = 10 ** (log_infections_fit)

    return log_infections_fit, infections_fit


def make_dates(df: pd.DataFrame, start_date: str, end_date: str):
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
    else:
        start_date = df.index[0]
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
    else:
        end_date = df.index[-1]
    return start_date, end_date
