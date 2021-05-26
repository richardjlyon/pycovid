from pycovid.data_utils.cmi import read_CMI_cumulative_SMR, read_CMI_SMR
from pytest import approx

DATA_FILE = "Mortality-monitor-spreadsheet-Q1-2021-v01-2021-04-13.xlsx"


def test_read_cumulative():
    df = read_CMI_cumulative_SMR(
        filename=DATA_FILE, gender="Unisex", age_range="20to100"
    )
    assert df[2020].loc[1] == approx(0.0000468, abs=1e-6)


def test_read_SMR():
    df = read_CMI_SMR(filename=DATA_FILE, smr_set="weekly")
    assert df.loc[("Unisex", "20to100", 1999)][31] == approx(0.015652)
    assert df.loc[("Male", "0to64", 2020)][1] == approx(0.00185211)
    assert df.loc[("Female", "15to44", 2010)][28] == approx(0.0004409949)
