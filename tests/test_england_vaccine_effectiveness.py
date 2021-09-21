from src.england_vaccine_effectiveness import VaccineData, InfectionData
import pandas as pd
import pytest
from datetime import datetime

v = VaccineData(week_no=37)
i = InfectionData()


class TestVaccineData:
    def test_initialise(self):
        assert isinstance(v.df.columns, pd.MultiIndex)

    @pytest.mark.parametrize(
        "is_under_50, date, expected",
        [
            (True, datetime(2021, 1, 3), 39919843),
            (True, datetime(2021, 7, 22), 39919843),
            (False, datetime(2021, 8, 30), 22336445),
        ],
    )
    def test_people_in_cohort(self, is_under_50, date, expected):
        assert v.cohort(is_under_50=is_under_50, date=date) == expected

    @pytest.mark.parametrize(
        "is_under_50, date, is_double, expected",
        [
            (True, datetime(2021, 7, 22), True, 10361734),
            (False, datetime(2021, 8, 30), False, 20375394),
        ],
    )
    def test_vaccinated(self, is_under_50, date, is_double, expected):
        assert (
            v.vaccinated(is_under_50=is_under_50, date=date, is_double=is_double)
            == expected
        )

    @pytest.mark.parametrize(
        "is_under_50, date, is_double, expected",
        [
            (True, datetime(2021, 7, 22), True, 39919843 - 10361734),
            (False, datetime(2021, 8, 30), False, 22336445 - 20375394),
        ],
    )
    def test_unvaccinated(self, is_under_50, date, is_double, expected):
        assert (
            v.unvaccinated(is_under_50=is_under_50, date=date, is_double=is_double)
            == expected
        )


class TestInfectionData:
    @pytest.mark.parametrize(
        "date, is_under_50, measure, expected",
        [
            (datetime(2021, 6, 25), True, "Dose 2 >= 14 days", 5600),
            (datetime(2021, 7, 19), True, "Unvaccinated", 119063),
            (datetime(2021, 8, 20), False, "Dose 1 < 21 days", 277),
        ],
    )
    def test_cases(self, date, is_under_50, measure, expected):
        cases = i.cases(date=date, is_under_50=is_under_50, measure=measure)
        assert cases == expected


# def test_infection_rate():
#     assert (v.infection_rate(is_under_50=True, date=datetime(2021, 7, 22), is_double=True)) ==
