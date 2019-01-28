from .auth import get_client
from .utils import clean_currency
import pandas as pd
from cachier import cachier


@cachier(pickle_reload=True)
def get_spreadsheet():
    client = get_client()
    return client.open("saisie_db")


@cachier()
def get_worksheet(worksheet_name):
    spreadsheet = get_spreadsheet()
    return spreadsheet.worksheet_by_title(worksheet_name)


@cachier()
def get_worksheet_as_df(worksheet_name):
    return pd.DataFrame(get_worksheet(worksheet_name).get_all_records())

