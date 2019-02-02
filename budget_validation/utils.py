import base64
from io import BytesIO

import arabic_reshaper
import numpy as np
import pandas as pd
from bidi.algorithm import get_display


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

