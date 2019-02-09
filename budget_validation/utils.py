import arabic_reshaper
import numpy as np
import pandas as pd
from bidi.algorithm import get_display


def clean_currency(string):
    if "TND" in string:
        currency_string = string.replace("TND", "").replace(",", "")
    else:
        currency_string = string.replace(",", ".")
    return np.round(pd.to_numeric(currency_string, errors="coerce"), 3)


def list_to_dropdown_options(lst):
    return sorted(
        [{"label": val, "value": val} for val in lst], key=lambda i: i["value"]
    )


def reshape(string):
    return get_display(arabic_reshaper.reshape(string))
