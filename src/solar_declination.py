import math

import matplotlib.pyplot as plt
import pandas as pd
from pycovid import OUTPUT_DIR
from pycovid.data_utils import prepare_owid_data

DATASOURCE = "owid-covid-data-uk-india.csv"


def declination_angle(date: pd.Timestamp) -> float:
    """Compute the declination angle in radians for day n, 1 Jan = 1."""
    n = date.day_of_year
    return 23.5 * math.cos(2 * math.pi * (n - 172) / 365)


def compute_declination(start_date: str, end_date: str) -> pd.DataFrame:

    df = pd.DataFrame(index=pd.date_range(start_date, end_date))
    df["solar angle"] = df.index.map(declination_angle)
    df_summer = df.loc[df["solar angle"] >= 0]
    df_winter = df.loc[df["solar angle"] <= 0]
    df = pd.DataFrame(pd.concat([df_winter, df_summer], axis=1))
    df.columns = ["solar angle (winter)", "solar angle (summer)"]

    return df


def plot_data(df: pd.DataFrame):
    fig, ax1 = plt.subplots(1, 1)
    ax2 = ax1.twinx()

    fig.set_size_inches(16, 8)
    fig.patch.set_facecolor("white")
    fig.suptitle("COVID-19 deaths versus solar declination")

    ax1.set_ylabel("Deaths (per million)")
    ax2.set_ylabel("Solar declination (degrees)")

    ax1.annotate(
        "richardlyon.substack.com SOURCE: Our World In Data 'COVID-19 Data Explorer'",
        (0, 0),
        (-50, -50),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="lightgrey",
    )

    ax1.plot(df.index, df["UK"], color="tab:green", label="UK (Northern Temperate)")
    ax1.fill_between(df.index, df["UK"], color="tab:green", alpha=0.1)

    ax1.plot(
        df.index, df["India"], color="tab:purple", label="India (Northern Tropical)"
    )
    ax1.fill_between(df.index, df["India"], color="tab:purple", alpha=0.1)

    ax2.plot(
        df.index,
        df["solar angle (winter)"],
        color="tab:blue",
        # label="solar angle (winter)",
    )
    ax2.fill_between(df.index, df["solar angle (winter)"], color="tab:blue", alpha=0.1)
    ax2.plot(
        df.index,
        df["solar angle (summer)"],
        color="tab:orange",
        # label="Solar declination (summer)",
    )
    ax2.fill_between(
        df.index, df["solar angle (summer)"], color="tab:orange", alpha=0.1
    )

    ax1.legend(loc="upper left")
    # ax2.legend(loc="upper right")

    plt.savefig(OUTPUT_DIR / "COVID-19 deaths vs solar declination.png")


if __name__ == "__main__":

    df_deaths = prepare_owid_data(DATASOURCE)
    df_solar = compute_declination("1 Feb 2020", "16 May 2021")
    df = pd.concat([df_deaths, df_solar], axis=1)

    plot_data(df)
