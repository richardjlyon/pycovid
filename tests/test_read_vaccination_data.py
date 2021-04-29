from pycovid.data_utils import read_vaccination_data


def test_read_vaccination_data():
    filename = "COVID-19-monthly-announced-vaccinations-15-April-2021-revised.xlsx"
    df = read_vaccination_data(filename)
    assert df["Total doses"].sum() == 1434642902
