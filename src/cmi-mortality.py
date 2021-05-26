"""
cmi-mortality.py

Institute and Faculty of Actuaries "Continuous Mortality Invectigation" unit corrects ONS data for
population size, age, and gender and publishes weekly and quarterly reports of trends. They recently
replaced the baseline for their 2020/21 from the 10 year average to 2019 - the lowest mortality on
record. This visualisation restores the 10 year baseline.

https://www.actuaries.org.uk/learn-and-develop/continuous-mortality-investigation/other-cmi-outputs/mortality-monitor
"""

from pycovid.data_utils.cmi import (
    read_CMI_mortality_monitor_spreadsheet,
    read_CMI_cumulative_SMR,
)
import matplotlib.pyplot as plt

DATA_FILE = "Mortality-monitor-spreadsheet-Q1-2021-v01-2021-04-13.xlsx"


def plot_smr_cum():
    df = read_CMI_cumulative_SMR(filename=DATA_FILE)
    df.plot()


def plot_smr():
    df = read_CMI_mortality_monitor_spreadsheet(
        filename=DATA_FILE, smrset="weekly", gender="U", age_range="0to64"
    )
    df_2021 = df.loc["2021-01-01":]

    df_2021["cum"] = df_2021["U_0to64"].cumsum()
    df_2021.plot()


if __name__ == "__main__":
    plot_smr_cum()
    plt.show()
