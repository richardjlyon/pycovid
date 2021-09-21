"""
    effectiveness.py

    Plot the efficacy and effectiveness of a vaccine based on published values of cases vaccinated and population
    vaccinated.

    See:
    - https://www.linkedin.com/posts/siglaugsson_how-well-do-the-vaccines-actually-work-do-activity-6828808152457216000-bOGW
    - https://www.who.int/news-room/feature-stories/detail/vaccine-efficacy-effectiveness-and-protection
"""
import numpy as np
from matplotlib import pyplot as plt

X = np.linspace(0.1, 1, 500)  # Proportion of Population Vaccinated (PPV)
# A = np.linspace(0.2, 0.8, 4)  # Proportion of Cases Vaccinated (PCV)
A = [0.5]


def ve(ppv, pcv):
    try:
        # return 1 - pcv / (1 - pcv) * ((1 - ppv) / ppv) + 100
        print(ppv)
        print(pcv)
        return (pcv / (1 - pcv)) * ((1 - ppv) / ppv)
    except:
        return None


def do_plot():
    fig, ax = plt.subplots(1, 1)
    ax.legend(loc="upper left")
    ax.set_xlabel("Proportion of Population Vaccinated (PPV)")
    ax.set_ylabel("Vaccine effectiveness")

    for a in A:
        plt.plot(X, ve(X, a), label=str(int(a * 100) / 100))

    ax.legend()
    plt.show()


if __name__ == "__main__":

    do_plot()
