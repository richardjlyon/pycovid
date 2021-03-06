"""
npi_effectiveness.py

Prepare a series of plots for exploring the relationship (if any) between COVID-19 fatal infection rate in England, Non
Pharmaceutical Interventions, and vaccination doses.
"""

import matplotlib.pyplot as plt
import pandas as pd
from pycovid import OUTPUT_DIR
from pycovid.chart_utils import (
    create_figure,
    FitItem,
    RegionItem,
    EventItem,
    LabelOrigin,
)
from pycovid.data_utils import polyfit
from pycovid.data_utils.nhs import read_vaccination_data
from pycovid.data_utils.ons import prepare_fatal_infection_data, XLMeta

SERIES_NAME = "NPI Effectiveness"


def plot_overview(df: pd.DataFrame):

    # fitted lines ######################################################################

    # regions ######################################################################

    regions = []

    regions.append(
        RegionItem(
            "2020-01-01",
            "2020-06-30",
            "tab:green",
            "2019/20 winter respiratory infection cycle",
        )
    )
    regions.append(
        RegionItem(
            "2020-07-01",
            "2021-04-28",
            "tab:blue",
            "2020/21 winter respiratory infection cycle",
        )
    )

    # events #######################################################################

    # OK. Go! ######################################################################

    create_figure(
        "Fatal COVID-19 Infections England 2020/21 vs. seasonal respiratory infection winter cycle",
        df,
        regions=regions,
        show_deaths=True,
        show_vaccinations=False,
    )

    plt.savefig(OUTPUT_DIR / f"{SERIES_NAME} - Fig 1 Overview.png")


def plot_2020(df: pd.DataFrame):

    df = df.loc["1 Jan 2020":"31 Jul 2020"]

    # fitted lines ######################################################################

    fits = []

    log_infection, infection = polyfit(
        df["infections (log)"], "20 Mar 2020", "23 Jun 2020"
    )
    fits.append(FitItem(log_infection, infection, "tab:red"))

    # regions ######################################################################

    regions = []

    regions.append(
        RegionItem("23 Jun 2020", "15 Aug 2020", "tab:orange", "2020 heatwave")
    )

    # events #######################################################################

    events = []

    events.append(EventItem("2020-03-26", "Lockdown #1"))
    events.append(EventItem("2020-04-30", "'Past the peak'"))
    events.append(EventItem("2020-05-10", "Restrictions relaxed"))
    events.append(EventItem("2020-06-1", "School reopens"))
    events.append(EventItem("2020-06-15", "Retail reopens"))
    events.append(EventItem("2020-06-23", "Restrictions relaxed"))
    events.append(EventItem("2020-07-04", "Pubs, restaurants, bars reopen"))

    # OK. Go! ######################################################################
    create_figure(
        "Fatal COVID-19 Infections England 2020 vs. key Non Pharmaceutical Interventions",
        df,
        fits=fits,
        regions=regions,
        events=events,
    )

    plt.savefig(OUTPUT_DIR / f"{SERIES_NAME} - Fig 2 2020.png")


def plot_2020_2021(df: pd.DataFrame):

    df = df.loc["1 Jul 2020":"10 Mar 2021"]

    # fitted lines ######################################################################

    fits = []

    log_infection, infection = polyfit(
        df["infections (log)"], "1 Aug 2020", "10 Oct 2020"
    )
    fits.append(FitItem(log_infection, infection, "tab:blue"))

    log_infection, infection = polyfit(
        df["infections (log)"], "12 Jan 2021", "8 Mar 2021"
    )
    fits.append(FitItem(log_infection, infection, "tab:green"))

    # regions ######################################################################

    regions = []

    regions.append(
        RegionItem("23 Jun 2020", "15 Aug 2020", "tab:orange", "2020 heatwave")
    )
    regions.append(
        RegionItem("23 Dec 2020", "27 Dec 2020", "tab:red", "Christmas easing")
    )

    # events #######################################################################

    events = []

    events.append(EventItem("2020-08-03", "Eat out help out start"))
    events.append(EventItem("2020-08-14", "Further easing"))
    events.append(EventItem("2020-08-31", "Eat out help out end"))
    events.append(EventItem("2020-10-14", "3-Tier system"))
    events.append(EventItem("2020-11-05", "Lockdown #2"))
    events.append(EventItem("2020-12-02", "Lockdown #2 End"))
    events.append(EventItem("2020-12-21", "Tier 4 restrictions"))
    events.append(EventItem("2020-12-23", "Christmas easing"))
    events.append(EventItem("2021-01-06", "Lockdown #3"))

    # OK. Go! ######################################################################

    create_figure(
        "Fatal COVID-19 Infections England 2020/21 vs. key Non Pharmaceutical Interventions",
        df,
        fits=fits,
        regions=regions,
        events=events,
        show_vaccinations=False,
        label_origin=LabelOrigin(50, 320),
    )

    plt.savefig(OUTPUT_DIR / f"{SERIES_NAME} - Fig 3 2020_2021.png")


def plot_vaccination_detail(df: pd.DataFrame):

    file_name = "Fig 4 Vaccine detail"

    df = df.loc["1 Dec 2020":"31 Mar 2021"]

    # fitted lines ######################################################################

    fits = []

    log_infection, infection = polyfit(
        df["infections (log)"], "11 Jan 2021", "8 Mar 2021"
    )
    fits.append(FitItem(log_infection, infection, "tab:green"))

    # regions ######################################################################

    regions = []

    regions.append(
        RegionItem("23 Dec 2020", "27 Dec 2020", "tab:red", "Christmas easing")
    )

    # events #######################################################################

    events = []

    events.append(EventItem("2020-12-23", "Christmas easing"))
    events.append(EventItem("2021-01-06", "Lockdown #3"))

    # OK. Go! ######################################################################

    create_figure(
        "COVID-19 Fatal Infection decline rate vs. vaccine doses (England)",
        df,
        fits=fits,
        regions=regions,
        events=events,
        show_vaccinations=True,
    )
    plt.savefig(OUTPUT_DIR / f"{SERIES_NAME} - {file_name}.png")

    datawrapper_df = df[["infections", "Vaccinations"]]
    datawrapper_df["infections - fit"] = infection
    datawrapper_df.to_csv(OUTPUT_DIR / f"{SERIES_NAME} - {file_name}.csv")


if __name__ == "__main__":
    meta = XLMeta(
        workbook="publishedweek282021.xlsx",
        region="England",
        start_row=4,
        end_row=506,
    )
    df = prepare_fatal_infection_data(meta)

    # df["Vaccinations"] = read_vaccination_data(
    #     workbook="COVID-19-daily-announced-vaccinations-28-July-2021.xlsx"
    # )

    plot_overview(df)
    plot_2020(df)
    plot_2020_2021(df)
    # plot_vaccination_detail(df)
