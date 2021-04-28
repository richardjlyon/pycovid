"""
npi_effectiveness.py

Poreare a series of plots for illustrating the relationship between COVID-19 fatal infection rate in England
with Non Pharmaceutical Interventions and vaccination doses to analyse correlation (if any).
"""

import matplotlib.pyplot as plt
import pandas as pd
from pycovid import OUTPUT_DIR
from pycovid.utils import (
    prepare_fatal_infection_data,
    read_vaccination_data,
    polyfit,
    create_figure,
    FitItem,
    RegionItem,
    EventItem,
)


def plot_2019_2020_infections(df: pd.DataFrame):

    fits = []
    regions = []
    events = []

    # fitted lines ######################################################################

    log_infection, infection = polyfit(
        df["infections (log)"], "20 Mar 2020", "23 Jun 2020"
    )
    fits.append(FitItem(log_infection, infection, "tab:red"))

    log_infection, infection = polyfit(
        df["infections (log)"], "15 Aug 2020", "10 Oct 2020"
    )
    fits.append(FitItem(log_infection, infection, "tab:blue"))

    log_infection, infection = polyfit(
        df["infections (log)"], "12 Jan 2021", "8 Mar 2021"
    )
    fits.append(FitItem(log_infection, infection, "tab:green"))

    # regions ######################################################################

    regions.append(
        RegionItem("23 Jun 2020", "15 Aug 2020", "tab:orange", "2020 heatwave")
    )
    regions.append(RegionItem("23 Dec 2020", "27 Dec 2020", "tab:red", "Christmas"))

    # events #######################################################################

    events.append(EventItem("2020-05-10", "Restrictions lifted"))
    events.append(EventItem("2020-06-1", "School reopens"))
    events.append(EventItem("2020-06-15", "Retail reopens"))
    events.append(EventItem("2020-06-23", "Relaxation of restrictions"))
    events.append(EventItem("2020-07-04", "Pubs, restaurants, bars reopen"))
    events.append(EventItem("2020-09-14", "Rule of 6"))
    events.append(EventItem("2020-09-22", "10pm curfew"))
    events.append(EventItem("2021-01-04", "return to school"))
    events.append(EventItem("2021-02-15", "Hotel quarantining"))

    # OK. Go! ######################################################################

    create_figure(
        "Fatal COVID-19 Infections England 2020/21 vs. Non Pharmaceutical Interventions and vaccination",
        df,
        fits,
        regions,
        events,
    )

    plt.savefig(OUTPUT_DIR / "2020 2021 infections vs NPIs.png")


def plot_winter_seasons(df: pd.DataFrame):
    fits = []
    regions = []
    events = []

    # regions ######################################################################

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

    events.append(EventItem("2020-03-26", "Lockdown #1"))
    events.append(EventItem("2020-04-30", "'Past the peak'"))
    events.append(EventItem("2020-08-03", "Eat out help out"))
    events.append(EventItem("2020-08-14", "Further easing"))
    events.append(EventItem("2020-10-14", "3-Tier system"))
    events.append(EventItem("2020-11-05", "Lockdown #2"))
    events.append(EventItem("2020-12-02", "Lockdown #2 End"))
    events.append(EventItem("2020-12-21", "Tier 4 restrictions"))
    events.append(EventItem("2021-01-06", "Lockdown #3"))

    # OK. Go! ######################################################################
    create_figure(
        "Fatal COVID-19 Infections England 2021 vs. northern hemisphere winter respiratory infection cycles",
        df,
        regions=regions,
        events=events,
        show_vaccinations=False,
    )

    plt.savefig(OUTPUT_DIR / "Overall profile.png")


if __name__ == "__main__":
    df = prepare_fatal_infection_data(
        region="England", start_date="1 Feb 2020", end_date="28 Apr 2021"
    )
    df["Vaccinations"] = read_vaccination_data(
        "COVID-19-monthly-announced-vaccinations-15-April-2021-revised.xlsx"
    )

    plot_winter_seasons(df)
    plot_2019_2020_infections(df)

    # plt.show()
