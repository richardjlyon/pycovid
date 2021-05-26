import pandas as pd
from pycovid import DATA_DIR


def read_vaccination_data(workbook: str) -> pd.DataFrame:
    """Read NHS Vaccination data for England and return as a dataframe."""
    skiprows = list(range(12)) + list(range(100, 500))
    df = pd.read_excel(
        DATA_DIR / workbook,
        sheet_name="Vaccination Date",
        usecols="B,T",
        skiprows=skiprows,
        parse_dates=True,
        index_col=0,
    )
    df.columns = ["Total doses"]

    return df
