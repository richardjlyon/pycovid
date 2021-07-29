import pandas as pd
from pycovid import DATA_DIR


def prepare_owid_data(csvfile: str, country: str) -> pd.DataFrame:
    """Extract Our World In Data data and return as a dataframe."""

    filename = DATA_DIR / csvfile
    df_raw = pd.read_csv(
        filename,
        index_col="date",
        parse_dates=True,
        usecols=["date", "location", "new_deaths_smoothed_per_million"],
    )

    df_uk = df_raw[df_raw["location"].str.contains("United Kingdom")]

    if country is not None:
        df_country = df_raw[df_raw["location"].str.contains(country)]
        df = pd.DataFrame(
            pd.concat(
                [
                    df_uk["new_deaths_smoothed_per_million"],
                    df_country["new_deaths_smoothed_per_million"],
                ],
                axis=1,
            )
        )
        df.columns = ["UK", country]
    else:
        df = pd.DataFrame(
            {"Date": df_uk.index, "UK": df_uk["new_deaths_smoothed_per_million"]}
        )

    return df
