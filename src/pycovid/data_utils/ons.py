# ons.py

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from pycovid import DATA_DIR


def read_ONS_daily_registrations(workbook, skiprows) -> pd.DataFrame:
    """Read raw ONS data for daily deaths where COVID-19 is mentioned on the certificate."""
    cols = "A:P"
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


def compute_daterange(df: pd.DataFrame):
    """Extract the first and last date of the index of df and return as a daterange object."""

    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    return pd.date_range(start_date, end_date)


@dataclass
class XLMeta:
    """Class for transferring metadata about an ONS spreadsheet."""

    workbook: str
    region: str
    start_row: int
    end_row: int


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

    df = read_ONS_daily_registrations(workbook=filename, skiprows=skiprows)
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


def compute_skiprows(start, end) -> List[int]:
    """Compute the rows to skip when imprting an ONS spreadsheet."""
    return list(range(start - 1)) + list(range(end, end + 20))
