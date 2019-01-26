from .auth import get_client
from .utils import clean_currency
import pandas as pd


def get_spreadsheet():
    client = get_client()
    return client.open("saisie_db")


def get_worksheet(worksheet_name):
    spreadsheet = get_spreadsheet()
    return spreadsheet.worksheet_by_title(worksheet_name)


def load_budget():
    """
    Return a dataframe for budget validation
    TODO: improve API, make it DRY and general
    """
    budget_type = pd.DataFrame(get_worksheet("budget_type").get_all_records())
    budget_by_type = pd.DataFrame(get_worksheet("budget_by_type").get_all_records())
    budget = (
        pd.merge(
            left=budget_type,
            left_on="name",
            right=budget_by_type,
            right_on="budget_type_name",
        )
        .drop(
            columns=[
                "name_fr",
                "name_en",
                "name_ar",
                "parent_id",
                "id_x",
                "budget_type_id",
                "organization_id",
                "id_y",
                "description",
                "name",
            ]
        )
        .rename(columns={"parent_name": "budget_type_parent_name"})
        .pipe(
            lambda df: df.assign(
                budget_type_parent_name=df["budget_type_parent_name"].str.strip()
            )
        )
        .pipe(lambda df: df.assign(value=df["value"].str.strip()))
        .pipe(
            lambda df: df.assign(organization_name=df["organization_name"].str.strip())
        )
        .pipe(lambda df: df.assign(budget_type_name=df["budget_type_name"].str.strip()))
        .dropna(subset=["value"])
        .pipe(lambda df: df.assign(value=clean_currency(df.value)))
    )
    return budget
