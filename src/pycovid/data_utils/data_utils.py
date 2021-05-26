"""
data_utils.py

Utilities for preparing data for COVID-19 analysis.
"""


from typing import Tuple

import numpy as np
import pandas as pd


def polyfit(
    df: pd.Series, start_date: str, end_date: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute the polynomial fit for df between start_date and end_date.

    :param df: The data to polyfit
    :param start_date: The date of the start of the interpolation
    :param end_date: The date of the end of the interpolation
    :return: a tuple containing the fits for log(infection) and infection
    """

    # reduce time range
    df = df.loc[start_date:end_date]

    # compute model and predictor
    X = pd.Series(range(1, len(df) + 1), index=df.index)
    model = np.polyfit(X, df, 1)
    predict = np.poly1d(model)

    idx = pd.date_range(start=start_date, end=end_date)

    log_infections_fit = pd.DataFrame(predict(X), index=idx)
    infections_fit = 10 ** (log_infections_fit)

    return log_infections_fit, infections_fit
