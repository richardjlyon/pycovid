from src.england_vaccine_effectiveness import VaccineData, InfectionData
import pandas as pd
from datetime import datetime

v = VaccineData(week_no=37)
i = InfectionData()


class TestVaccineData:
    def test_initialise(self):
        assert isinstance(v.df.columns, pd.MultiIndex)

    def test_people_in_cohort(self):
        assert v.cohort(is_under_50=True, date=datetime(2021, 1, 3)) == 39919843
        assert v.cohort(is_under_50=True, date=datetime(2021, 7, 22)) == 39919843
        assert v.cohort(is_under_50=False, date=datetime(2021, 8, 30)) == 22336445

    def test_vaccinated(self):
        assert (
            v.vaccinated(is_under_50=True, date=datetime(2021, 7, 22), is_double=True)
            == 10361734
        )
        assert (
            v.vaccinated(is_under_50=False, date=datetime(2021, 8, 30), is_double=False)
            == 20375394
        )

    def test_unvaccinated(self):
        assert (
            v.unvaccinated(is_under_50=True, date=datetime(2021, 7, 22), is_double=True)
            == 39919843 - 10361734
        )
        assert (
            v.unvaccinated(
                is_under_50=False, date=datetime(2021, 8, 30), is_double=False
            )
            == 22336445 - 20375394
        )


class TestInfectionData:
    def test_initialise(self):

        print(i.df)
        assert (
            i.df.loc[datetime(2021, 6, 25)]["<50"]["Dose 1 < 21 days"].iloc[0] == 8453
        )
        assert (
            i.df.loc[datetime(2021, 9, 3)][">=50"]["Dose 2 >= 14 days"].iloc[0] == 71991
        )

    def test_cases(self):
        cases = i.cases(
            date=datetime(2021, 6, 21), measure="Unvaccinated", is_under_50=True
        )
        # print(df)
        assert cases == 70664


# def test_infection_rate():
#     assert (v.infection_rate(is_under_50=True, date=datetime(2021, 7, 22), is_double=True)) ==
