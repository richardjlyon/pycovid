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
