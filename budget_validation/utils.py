import base64
from io import BytesIO

import arabic_reshaper
import numpy as np
import pandas as pd
from bidi.algorithm import get_display
import matplotlib.pyplot as plt


def clean_currency(col):
    ill_formatted_numbers = col.apply(lambda val: "TND" not in str(val))
    col.loc[ill_formatted_numbers].apply(lambda val: val.replace(",", "."))
    return pd.to_numeric(col.str.replace("TND", "").str.replace(",", "")).apply(
        lambda val: np.round(val, 3)
    )


def list_to_dropdown_options(lst):
    return sorted(
        [{"label": val, "value": val} for val in lst], key=lambda i: i["value"]
    )


def reshape(string):
    return get_display(arabic_reshaper.reshape(string))


# from https://github.com/4QuantOSS/DashIntro/blob/master/notebooks/Tutorial.ipynb
def fig_to_uri(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format="png", **save_args)
    if close_all:
        in_fig.clf()
        plt.close("all")
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)
