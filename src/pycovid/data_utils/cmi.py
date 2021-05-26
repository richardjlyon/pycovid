import pandas as pd
from pycovid import DATA_DIR

SETS = {
    "weekly": "WeeklySMR",
    "quarterly": "WeeklySMR13",
    "annual": "WeeklySMR53",
}
GENDERS = {"Unisex": "A:N", "Male": "A:D,T:AC", "Female": "A:N,AI:AR"}
AGE_RANGES = [
    "20to100",
    "0to64",
    "65to84",
    "85plus",
    "Under1",
    "1to14",
    "15to44",
    "45to64",
    "65to74",
    "75to84",
]


def compute_cols_for_gender_agerange(gender: str) -> str:
    """Compute spreadsheet column names from supplied gender."""
    return [f"{gender[0]}_{age_range}" for age_range in AGE_RANGES]


def read_CMI_SMR(filename: str, smr_set: str):
    """
    Create dataframe, index ["Gender", "AgeBand", "Year"] column "Week number"
    :param filename:
    :param gender:
    :param age_range:
    :param smr_set:
    :return:
    """
    if smr_set not in SETS.keys():
        raise AttributeError(f"set not in {list(SETS.keys())}: got {smr_set}")

    FILE = DATA_DIR / "CMI" / filename

    # Create dataframe, index ["Gender", "AgeBand", "Year"], column "Week number"

    df_raw = pd.read_excel(
        FILE, sheet_name=SETS.get(smr_set), usecols="C:N, T:AC, AI:AR"
    )

    # construct a dataframe from each gender
    df = pd.DataFrame()
    for gender in GENDERS.keys():
        cols = ["ISOWeek", "ISOYear"] + compute_cols_for_gender_agerange(gender)
        df_gender = df_raw[cols]

        old_cols = df_gender.columns
        new_cols = ["ISOWeek", "ISOYear"] + [
            col[2:] for col in old_cols[2:] if "_" in col
        ]
        df_gender.columns = new_cols

        df_gender["Gender"] = gender
        df = df.append(df_gender)

    # reshape
    df = df.pivot(index=["Gender", "ISOYear"], columns="ISOWeek")
    df = df.swaplevel(axis=1)
    df = df.stack()
    df = df.rename_axis(["Gender", "Year", "AgeBand"])
    df = df.swaplevel().sort_index()

    return df


def read_CMI_cumulative_SMR(
    filename: str,
    gender: str,
    age_range: str,
    relative: bool = False,
) -> pd.DataFrame:
    """
    Read the Cumulative SMR for the given gender and age range.
    :return: Cumulative SMR for each year, indexed on ISO day number
    """
    GENDERS = ["Unisex", "Male", "Female"]

    if gender not in GENDERS:
        raise AttributeError(f"gender not in {GENDERS}: got {gender}")
    if age_range not in AGE_RANGES:
        raise AttributeError(f"age range not in {AGE_RANGES}: got {age_range}")
    if relative:
        sheetname = "CumulativeSMRRelative"
    else:
        sheetname = "CumulativeSMR"

    FILE = DATA_DIR / "CMI" / filename
    df_raw = pd.read_excel(
        FILE,
        sheet_name=sheetname,
        usecols="A:C, F:NG",
        index_col=[0, 1, 2],
    )

    df = df_raw.loc[(gender, age_range)].T

    return df
