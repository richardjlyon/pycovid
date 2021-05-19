"""
data_utils.py

Utilities for preparing data for COVID-19 analysis.
"""


from typing import Tuple, List
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pycovid import DATA_DIR


@dataclass
class XLMeta:
    """Class for transferring metadata about an ONS spreadsheet."""

    workbook: str
    region: str
    start_row: int
    end_row: int


def compute_skiprows(start, end) -> List[int]:
    """Compute the rows to skip when imprting an ONS spreadsheet."""
    return list(range(start - 1)) + list(range(end, end + 20))


def compute_daterange(df: pd.DataFrame):
    """Extract the first and last date of the index of df and return as a daterange object."""

    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    return pd.date_range(start_date, end_date)


def read_daily_registrations(workbook, skiprows, cols) -> pd.DataFrame:
    """Read raw ONS data for daily deaths where COVID-19 is mentioned on the certificate."""
    df = pd.read_excel(
        workbook,
        sheet_name="Covid-19 - Daily registrations",
        usecols=cols,
        skiprows=skiprows,
    )

    daterange = compute_daterange(df)

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


def prepare_fatal_infection_data(meta: XLMeta) -> pd.DataFrame:
    """
    Construct a timeseries dataframe of fatal infections.

    Fatal infection rate is computed by timeshifting COVID-19 registered fatalities. Fatalities are not recorded at
    weekends, so we smooth the raw data with a rolling window.

    :return: a dataframe of smoothed fatal infection rate and log fatal infection rate
    """

    INFECTION_TO_DEATH_DAYS = 28

    # get the raw death data #####################################################

    filename = DATA_DIR / meta.workbook
    skiprows = compute_skiprows(meta.start_row, meta.end_row)
    cols = "A:P"

    df = read_daily_registrations(workbook=filename, skiprows=skiprows, cols=cols)
    total_deaths = df[meta.region].sum()

    # compute fatal infection from death #########################################

    # extend dates to allow deaths to be shifted forward by INFECTION_TO_DEATH_DAYS
    idx = pd.date_range(
        df.index[0] - pd.Timedelta(days=INFECTION_TO_DEATH_DAYS), df.index[-1]
    )
    df = df.reindex(idx)

    # compute fatal infections
    infections = df[meta.region].shift(periods=-INFECTION_TO_DEATH_DAYS)

    # smooth: this discards a small number of infections, so scale back up
    infections_smoothed = infections.rolling(window=7, center=True).mean()
    correction_factor = infections.sum() / infections_smoothed.sum()
    infections_smoothed *= correction_factor
    assert abs(infections_smoothed.sum() / total_deaths) > 0.9999999

    # log
    infections_log = np.log10(infections_smoothed)

    # construct dataframe
    data = {
        "deaths (raw)": df[meta.region],
        "infections": infections_smoothed,
        "infections (log)": infections_log,
    }
    df = pd.concat(data, axis=1)

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
