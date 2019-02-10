import inspect

import dash
import numpy as np
import pandas as pd


# !CREDIT: https://github.com/ned2/slapdash/blob/master/src/slapdash/utils.py
def get_dash_args_from_flask_config(config):
    """
    Get a dict of Dash parameters specified in the Flask config.

    Arguments:
        config {Flask config} -- configuration loaded by flask

    Returns:
        dict -- a dictionary of configuration keys accepted by Dash

    """
    # all arg names except for 'self'
    dash_args = set(inspect.getfullargspec(dash.Dash.__init__).args[1:])
    return {key.lower(): val for key, val in config.items() if key.lower() in dash_args}


def get_dash_runserver_args_from_flask_config(config):
    """
    Get a dict of Dash runserver parameters specified in the Flask config.

    Arguments:
        config {Flask config} -- configuration loaded by flask
    Returns:
        dict -- a dictionary of configuration keys accepted by Dash run_server

    """
    # all arg names except for 'self'
    dash_runserver_args = set(inspect.getfullargspec(dash.Dash.run_server).args[1:])
    return {
        key.lower(): val
        for key, val in config.items()
        if key.lower() in dash_runserver_args
    }


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
