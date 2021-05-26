"""
decline_comparison.py

Prepare a plot that compares the 2020 and 2021 post-peak declines to analyse decline rates and assess the impact of
vaccine (if any).
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pycovid import OUTPUT_DIR
from pycovid.data_utils.nhs import read_vaccination_data
from pycovid.data_utils.ons import prepare_fatal_infection_data, XLMeta


def isolate_declines():
    global df
    """Isolate declines, normalise, and timeshift to overlay them."""

    # make room
    idx = pd.date_range("1 Jan 2020", "31 Mar 2021")
    df = df.reindex(idx)

    df_2020 = df["infections"].loc["20 Mar 2020":"31 Jul 2020"]
    df_2020 = df_2020 / df_2020.max()
    df_2020.reset_index(drop=True, inplace=True)

    df_2021 = df["infections"].loc["15 Jan 2021":"30 Apr 2021"]
    df_2021 = df_2021 / df_2021.max()
    df_2021.reset_index(drop=True, inplace=True)

    df_vaccination = df["Vaccinations"]["11 jan 2021":]
    df_vaccination = df_vaccination.shift(periods=4)  # align with day 0 of peak
    df_vaccination.reset_index(drop=True, inplace=True)

    data = {
        "2020": df_2020,
        "2020 (log)": np.log10(df_2020),
        "2021": df_2021,
        "2021 (log)": np.log10(df_2021),
        "vaccinations": df_vaccination,
    }
    df = pd.concat(data, axis=1)

    return df


def fit_lines(df_sample):

    model = np.polyfit(df_sample.index, df_sample, 1)
    predict = np.poly1d(model)
    log_fit = pd.DataFrame(predict(df_sample.index), index=df_sample.index)
    fit = 10 ** log_fit

    return log_fit, fit


if __name__ == "__main__":
    meta = XLMeta(
        workbook="publishedweek1820211.xlsx",
        region="England",
        start_row=4,
        end_row=436,
    )
    df = prepare_fatal_infection_data(meta)

    df["Vaccinations"] = read_vaccination_data(
        workbook="COVID-19-monthly-announced-vaccinations-15-April-2021-revised.xlsx"
    )

    df = isolate_declines()

    samples = [(2020, df["2020 (log)"][:90]), (2021, df["2021 (log)"][:50])]
    for year, sample in samples:
        log_fit, fit = fit_lines(sample)
        df[f"{year} (log fit)"] = log_fit
        df[f"{year} (fit)"] = fit

    # plot ########################################

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax3 = ax2.twinx()
    fig.set_size_inches(16, 5)
    fig.set_tight_layout(True)
    fig.patch.set_facecolor("white")
    fig.suptitle("Fatal COVID-19 infection - post peak decline comparison (England)")

    ax1.annotate(
        "richardlyon.substack.com",
        (0, 0),
        (-50, -50),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="lightgrey",
    )

    # plot fatal infections (left panel)
    alpha = 0.2
    ax1.plot(df.index, df["2020"], color="tab:red", alpha=alpha)
    ax1.plot(df.index, df["2020 (fit)"], label="2020", color="tab:red")
    ax1.plot(df.index, df["2021"], color="tab:green", alpha=alpha)
    ax1.plot(df.index, df["2021 (fit)"], label="2021", color="tab:green")
    ax1.set_ylabel("fatal infections (normalised)")
    ax1.set_xlabel("Days from peak")

    ax2.semilogy(df.index, df["2020"], color="tab:red", alpha=alpha)
    ax2.semilogy(df.index, df["2020 (fit)"], label="2020", color="tab:red")
    ax2.semilogy(df.index, df["2021"], color="tab:green", alpha=alpha)
    ax2.semilogy(df.index, df["2021 (fit)"], label="2021", color="tab:green")
    ax2.set_ylabel("fatal infections (logarithmic scale)")
    ax2.set_xlabel("Days from peak")

    df["vaccinations"] = df["vaccinations"] / 1e6
    ax3.set_ylabel("Total vaccination doses (million)", color="m")
    ax3.set_ylim([0, df["vaccinations"].max() * 2])
    ax3.plot(df["vaccinations"], color="m", label="2021 vaccination doses (total)")
    ax3.fill_between(
        x=df["vaccinations"].index,
        y1=0,
        y2=df["vaccinations"],
        color="m",
        alpha=0.05,
    )

    ax1.legend()
    ax2.legend()
    ax3.legend(loc="lower right")

    plt.savefig(OUTPUT_DIR / "Post peak comparison.png")
