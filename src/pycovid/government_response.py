"""
stringency.py

Get COVID-19 Government Response data from

Codes:
https://github.com/OxCGRT/covid-policy-tracker/blob/master/documentation/codebook.md

"""

import pandas as pd
from pycovid import DATA_DIR


def get_government_response(country_code: str = "GBR", policies=None) -> pd.DataFrame:
    data_file = DATA_DIR / "OxCGRT_latest.csv"
    df = pd.read_csv(data_file)

    df = df.loc[df["CountryCode"] == country_code]

    for policy in policies:
        df = df.loc[df[policy[0]] >= policy[1]]
    return df


def government_response(measures: List[str]) -> pd.DataFrame:
    """
    Get COVID-19 Government Response data (see: https://github.com/OxCGRT/covid-policy-tracker)
    :param index_name: The index to fetch (this is the tab name in the workbook)
    :return: a datafrom with the data as a timeseries
    """

    result = pd.DataFrame()

    for measure in measures:
        df = pd.read_excel(
            DATA_DIR / "OxCGRT_timeseries_all.xlsx",
            sheet_name=measure,
        )

        df = df[df["country_code"] == "GBR"].T
        df = df.drop(["country_code", "country_name"])
        df.index = pd.to_datetime(df.index)
        df.rename(columns={61: measure}, inplace=True)

        # result.index = pd.to_datetime(df.index)
        result = pd.concat([result, df], axis=1)

    return result
