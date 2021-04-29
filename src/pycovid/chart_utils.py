"""
chart_utils.py

Utilities for preparing charts for COVID-19 analysis.
"""

from dataclasses import dataclass, InitVar

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter, datestr2num
from typing import List


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


def create_figure(
    title: str,
    df: pd.DataFrame,
    fits: List[FitItem] = [],
    regions: List[RegionItem] = [],
    events: List[EventItem] = [],
    show_deaths=False,
    show_vaccinations=False,
):
    """Create a side-by-side figure of fatal infections and (optionally) vaccinations, with overlays."""

    fig, (ax1, ax2) = plt.subplots(1, 2)
    if show_vaccinations:
        ax3 = ax2.twinx()
    else:
        ax3 = None
    fig.set_size_inches(16, 5)
    fig.set_tight_layout(True)
    fig.patch.set_facecolor("white")
    fig.suptitle(title)

    ax1.annotate(
        "richardlyon.substack.com",
        (0, 0),
        (-50, -50),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="lightgrey",
    )

    # set x axis date label format
    for ax in (ax for ax in [ax1, ax2, ax3] if ax is not None):

        ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_major_formatter(DateFormatter("\n%Y"))
        ax.xaxis.set_minor_locator(
            MonthLocator((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        )
        ax.xaxis.set_minor_formatter(DateFormatter("%b"))

    # plot fatal infections (left panel)
    if show_deaths:
        ax1.plot(df.index, df["deaths (raw)"], color="lightgrey", label="deaths (raw)")
        ax1.plot(df.index, df["infections"], color="tab:blue", label="fatal infections")
    else:
        ax1.plot(df.index, df["infections"], color="lightgrey")
    ax1.set_ylabel("fatal infections")
    ax1.set_ylim([0, 1400])

    # plot log(fatal infections) (right panel)
    if show_deaths:
        color = "tab:blue"
    else:
        color = "lightgrey"
    ax2.plot(df.index, df["infections (log)"], color=color)
    ax2.set_ylabel("log(fatal infections)")
    ax2.set_ylim([0, df["infections (log)"].max() * 1.05])

    # plot vaccinations
    if show_vaccinations:
        ax3.set_ylabel("Total vaccination doses (million)", color="m")
        ax3.set_ylim([0, df["Vaccinations"].max() / 1e6 * 2])
        ax3.plot(df["Vaccinations"] / 1e6, color="m")
        ax3.fill_between(
            x=df["Vaccinations"].index,
            y1=0,
            y2=df["Vaccinations"] / 1e6,
            color="m",
            alpha=0.1,
        )

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
            xytext=(x, 1150),
            textcoords="data",
            arrowprops=dict(arrowstyle="-|>"),
        )
        ax2.annotate(
            f"{i+1} {event.label}",
            (x, y2),
            xytext=(200, 180 - i * 20),
            textcoords="axes pixels",
            arrowprops=dict(arrowstyle="-|>"),
        )

    ax1.legend(loc="upper center")
