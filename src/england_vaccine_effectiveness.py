"""
    england_vaccine_effectiveness.py

    Does the vaccine significantly reduce the risk of infection?

    This script computes the vaccine effectiveness for (i) over 50 yo (ii) under 50 yo and generates a report
    summarising variation over time.

    See data/England vaccine effectiveness/README.md

"""
from src.pycovid import DATA_DIR
import pandas as pd
from datetime import datetime


pd.options.mode.chained_assignment = None  # default='warn'

UNDER_50 = ["Under 40", "40 to under 45", "45 to under 50"]

OVER_50 = [
    "50 to under 55",
    "55 to under 60",
    "60 to under 65",
    "65 to under 70",
    "70 to under 75",
    "75 to under 80",
    "Over 80",
]


class VaccineData:
    """
    Represents NHS vaccine data set. Provides the cohort population and numbers vaccinated and unvaccinated on
    a given date.
    """

    def __init__(self, week_no: int):
        filename = (
            DATA_DIR
            / "England vaccine effectiveness"
            / f"Weekly_Influenza_and_COVID19_report_data_w{week_no}.xlsx"
        )

        self.df = pd.read_excel(
            filename,
            sheet_name="Figure 61. COVID Vac Uptake",
            skiprows=7,
            header=[0, 1],
        )

        # filter out computed vaccine uptake
        COLS_TO_KEEP = [
            "Unnamed: 2_level_1",  # Note: 'Week Ending' has been imported as a multi index under this level name
            "People In NIMS Cohort",
            "Number Vaccinated (at least 1 dose)",
            "Number Vaccinated (2 Doses)",
        ]
        self.df = self.df.loc[:, (self.df.columns.levels[0], COLS_TO_KEEP)]

        # set index to 'Week Ending'
        self.df = self.df.set_index([("Week Ending", "Unnamed: 2_level_1")])
        self.df.index.rename("Week Ending", inplace=True)

    def cohort(self, is_under_50: bool, date: datetime) -> int:
        df = self._get_data_for_age_and_date(is_under_50, date)
        return df["People In NIMS Cohort"].sum()

    def vaccinated(self, is_under_50: bool, date: datetime, is_double: bool) -> int:
        df = self._get_data_for_age_and_date(is_under_50, date)

        if is_double:
            return df["Number Vaccinated (2 Doses)"].sum()
        else:
            return df["Number Vaccinated (at least 1 dose)"].sum()

    def unvaccinated(self, is_under_50: bool, date: datetime, is_double: bool) -> int:
        cohort = self.cohort(is_under_50, date)
        vaccinated = self.vaccinated(is_under_50, date, is_double)

        return cohort - vaccinated

    def _get_data_for_age_and_date(self, is_under_50: bool, date: datetime):
        if is_under_50:
            df = self.df[UNDER_50]
        else:
            df = self.df[OVER_50]

        df = df[df.index <= date].iloc[-1].swaplevel()

        return df


class InfectionData:
    """A class to represent a set of data about Delta cases in England."""

    def __init__(self):
        filename = (
            DATA_DIR
            / "England vaccine effectiveness"
            / "Delta Cases In England By Vaccination Status.xlsx"
        )
        self.df = pd.read_excel(
            filename,
            skiprows=1,
            parse_dates=[1],
            header=[0, 1],
        )

        self.df = self.df.set_index([("Date", "Unnamed: 1_level_1")])
        self.df.index.rename(("Date"), inplace=True)

    def cases(self, date: datetime, measure: str, is_under_50: bool) -> int:
        df = self.df[self.df.index <= date].iloc[-1]  # .swaplevel()
        print(df)

        return None

    def attack_rate(self, is_under_50: bool, vaccine_data: VaccineData) -> pd.DataFrame:

        if is_under_50:
            infection_df = self.df["<50"]
            vaccine_df = vaccine_data.df[UNDER_50]
        else:
            infection_df = self.df[">=50"]
            vaccine_df = vaccine_data.df[OVER_50]

        df = pd.DataFrame(index=infection_df.index)

        # compute case deltas

        MEASURES = [
            "Dose 1 < 21 days",
            "Dose 1 >= 21 days",
            "Dose 2 >= 14 days",
            "Unvaccinated",
        ]

        for measure in MEASURES:
            df[f"Δ {measure}"] = infection_df[measure] - infection_df[measure].shift(1)

        # compute vaccine status

        print(df)

        return df


if __name__ == "__main__":
    pass
