"""
utils.py

Utilities for COVID-19 analysis.
"""

from dataclasses import dataclass, InitVar
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter, datestr2num
from pycovid import DATA_DIR

DEFAULT_WORKBOOK = "publishedweek142021.xlsx"


@dataclass
class FitItem:
    """Class for passing fit data."""

    log_infection: pd.DataFrame
    infection: pd.DataFrame
    colour: str


@dataclass
class RegionItem:
    """Class for passing region data."""

    start: InitVar[str]
    end: InitVar[str]
    color: str
    label: str

    def __post_init__(self, start: str, end: str):
        self.x1 = pd.to_datetime(start)
        self.x2 = pd.to_datetime(end)


@dataclass
class EventItem:
    """Class for holding Non Pharmaceutical Event information."""

    date: str
    label: str


def read_daily_registrations(filename, skiprows, cols, daterange) -> pd.DataFrame:
    """Read raw ONS data for daily deaths where COVID-19 is mentioned on the certificate."""
    df = pd.read_excel(
        filename,
        sheet_name="Covid-19 - Daily registrations",
        usecols=cols,
        skiprows=skiprows,
    )

    # ONS date formatting is screwed: replace with generated dates
    df["Date"] = daterange
    df.set_index("Date", inplace=True)

    return df


def prepare_fatal_infection_data(
    region: str = "UK", start_date: str = None, end_date: str = None
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

    filename = DATA_DIR / DEFAULT_WORKBOOK
    skiprows = list(range(3)) + list(range(408, 425))
    cols = "A:P"
    daterange = pd.date_range(start="2 Mar 2020", end="9 Apr 2021")

    df = read_daily_registrations(
        filename=filename, skiprows=skiprows, cols=cols, daterange=daterange
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
        "infections": infections_smoothed,
        "infections (log)": infections_log,
    }
    df = pd.concat(data, axis=1)
    df = df.loc[(df.index >= start_date) & (df.index <= end_date)]

    return df


def read_vaccination_data(filename) -> pd.DataFrame:
    """Read NHS Vaccination data for England and return as a dataframe."""
    skiprows = list(range(12)) + list(range(100, 500))
    df = pd.read_excel(
        DATA_DIR / filename,
        sheet_name="Vaccination Date",
        usecols="B,T",
        skiprows=skiprows,
        parse_dates=True,
        index_col=0,
    )
    df.columns = ["Total doses"]

    return df


def polyfit(df: pd.Series, start_date, end_date) -> Tuple[pd.DataFrame, pd.DataFrame]:
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


def create_figure(
    title: str,
    df: pd.DataFrame,
    fits: List[FitItem] = [],
    regions: List[RegionItem] = [],
    events: List[EventItem] = [],
    show_vaccinations=True,
):
    """Create a side-by-side figure of fatal infections and (optionally) vaccinations, with overlays."""

    # plt.tight_layout()

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax3 = ax2.twinx()
    fig.set_size_inches(16, 5)
    fig.set_tight_layout(True)
    fig.patch.set_facecolor("white")
    fig.suptitle(title)

    # set x axis date label format
    for ax in [ax1, ax2, ax3]:

        ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_major_formatter(DateFormatter("\n%Y"))
        ax.xaxis.set_minor_locator(
            MonthLocator((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        )
        ax.xaxis.set_minor_formatter(DateFormatter("%b"))

    # plot fatal infections (left panel)
    ax1.plot(df.index, df["infections"], color="lightgrey")
    ax1.set_ylabel("fatal infections")

    # plot log(fatal infections) (right panel)
    ax2.plot(df.index, df["infections (log)"], color="lightgrey")
    ax2.set_ylabel("log(fatal infections)")
    ax2.set_ylim([0, df["infections (log)"].max() * 1.05])

    # plot vaccinations
    if show_vaccinations:
        ax3.set_ylabel("Vaccinations (million)", color="m")
        ax3.plot(df["Vaccinations"] / 1e6, color="m")
        ax3.fill_between(
            x=df["Vaccinations"].index,
            y1=0,
            y2=df["Vaccinations"] / 1e6,
            color="m",
            alpha=0.1,
        )

    ax3.set_ylim([0, df["Vaccinations"].max() / 1e6 * 2])

    for fit in fits:
        ax1.plot(fit.infection, color=fit.colour)
        ax2.plot(fit.log_infection, color=fit.colour)

    for region in regions:
        for ax in [ax1, ax2]:
            ax.axvspan(
                region.x1,
                region.x2,
                label=region.label,
                color=region.color,
                alpha=0.1,
            )

    for i, event in enumerate(events):
        x = datestr2num(event.date)
        y1 = df["infections"][event.date]
        y2 = df["infections (log)"][event.date]
        ax1.annotate(
            f"{i+1}",
            (x, y1),
            xytext=(x, 1100),
            textcoords="data",
            arrowprops=dict(arrowstyle="-|>"),
        )
        ax2.annotate(
            f"{i+1} {event.label}",
            (x, y2),
            xytext=(10, 180 - i * 20),
            textcoords="axes pixels",
            arrowprops=dict(arrowstyle="-|>"),
        )

    ax1.legend()


def make_dates(df, start_date, end_date):
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
    else:
        start_date = df.index[0]
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
    else:
        end_date = df.index[-1]
    return start_date, end_date
