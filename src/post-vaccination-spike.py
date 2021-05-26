"""
vaccine_odds_ratio.py

Visualises the odds ratio data presented in Public Health England's COVID-19 vaccine surveillance report Week 20
"""

import matplotlib.pyplot as plt
import pandas as pd
from pycovid import DATA_DIR, OUTPUT_DIR

DATA_DIR = DATA_DIR / "PHE_VACCINE_REPORT_20"

manufacturer = {
    1: "Pfizer-BioNTech",
    2: "AstraZeneca",
}


def make_title(figure, dose):
    return f"{manufacturer[figure]} Dose {dose}"


def read_csv(figure, dose):
    file = f"{DATA_DIR}/Fig_{figure}_Dose_{dose}.csv"
    df = pd.read_csv(file)
    df["day"] = df["d1"] + (df["d2"] - df["d1"]) / 2
    df.set_index(df["day"], inplace=True)

    return df["odds ratio"]


def plot():
    fig, ax1 = plt.subplots(1, 1)
    fig.set_size_inches(16, 8)
    fig.patch.set_facecolor("white")
    fig.suptitle("Odds ratio of becoming a case by days after vaccination (>65 yo)")

    ax1.set_ylabel("Odds Ratio")
    ax1.set_xlabel("Days after vaccination of onset")

    ax1.annotate(
        "richardlyon.substack.com SOURCE: PHE COVID-19 Vaccine surveillance report Week 20",
        (0, 0),
        (-50, -50),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="lightgrey",
    )

    ax1.annotate(
        "Increased risk",
        (0, 0),
        (400, 370),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="r",
    )

    ax1.annotate(
        "Reduced risk",
        (0, 0),
        (400, 240),
        xycoords="axes pixels",
        textcoords="offset pixels",
        va="top",
        color="g",
    )

    ax1.axhspan(1, 1.4, color="r", alpha=0.1)
    ax1.axhspan(0, 1.0, color="g", alpha=0.1)

    for fig in [1, 2]:

        if fig == 1:
            colour = "tab:blue"
        else:
            colour = "tab:orange"

        for dose in [1, 2]:

            if dose == 1:
                linestyle = "solid"
            else:
                linestyle = "dotted"

            title = make_title(fig, dose)
            df = read_csv(fig, dose)
            df = df.iloc[1:]
            ax1.plot(df.index, df, color=colour, linestyle=linestyle, label=title)

    ax1.legend()

    plt.savefig(OUTPUT_DIR / "post vaccination spike.png")


if __name__ == "__main__":
    plot()
