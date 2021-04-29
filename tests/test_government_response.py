from pycovid.data_utils import government_response
import matplotlib.pyplot as plt


def test_government_response():
    measures = [
        "c1_school_closing",
        "c2_workplace_closing",
        "c6_stay_at_home_requirements",
    ]
    df = government_response(measures)
    c2 = df["c1_school_closing"]
    c2 = c2[c2.pct_change().lt(0)]

    print(c2)

    df["c1_school_closing"].plot()
    plt.show()
