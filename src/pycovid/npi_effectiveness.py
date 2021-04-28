"""
npi_effectiveness.py

Compare England and Wales COVID-19 fatal infection rate with Non Pharmaceutical Interventions
and vaccination doses to analyse correlation (if any).
"""

import matplotlib.pyplot as plt
import pandas as pd
from pycovid.utils import (
    get_fatal_infections,
    read_vaccination_data,
    polyfit,
    create_figure,
    provision_plot,
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
        df["infections (log)"], "10 Jan 2021", "8 Mar 2021"
    )
    fits.append(FitItem(log_infection, infection, "tab:green"))

    # regions ######################################################################

    regions.append(
        RegionItem("23 Jun 2020", "15 Aug 2020", "tab:orange", "2020 heatwave")
    )
    regions.append(RegionItem("23 Dec 2020", "27 Dec 2020", "tab:red", "Christmas"))

    # events #######################################################################

    events.append(EventItem("2020-04-30", "'Past the peak'"))
    events.append(EventItem("2020-05-10", "restrictions lifted"))
    events.append(EventItem("2020-06-1", "school reopens"))
    events.append(EventItem("2020-06-15", "retail reopens"))
    events.append(EventItem("2020-06-23", "relaxation of restrictions"))
    events.append(EventItem("2020-07-04", "pubs, restaurants, bars reopen"))
    events.append(EventItem("2020-09-14", "Rule of 6"))
    events.append(EventItem("2020-09-22", "10pm curfew"))
    # events.append(EventItem("2021-01-04", "return to school"))
    events.append(EventItem("2021-02-15", "hotel quarantining"))

    # OK. Go! ######################################################################

    (ax1, ax2) = create_figure(
        "Fatal COVID-19 Infections England 2020/21 vs. Non Pharmaceutical Interventions"
    )
    provision_plot(ax1, ax2, df, fits, regions, events)


if __name__ == "__main__":
    df = get_fatal_infections(
        region="England", start_date="1 Feb 2020", end_date="28 Apr 2021"
    )

    df["Vaccinations"] = read_vaccination_data(
        "COVID-19-monthly-announced-vaccinations-15-April-2021-revised.xlsx"
    )

    plot_2019_2020_infections(df)

    plt.show()
