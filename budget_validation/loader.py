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


def clear_cache():
    for func in [get_spreadsheet, get_worksheet, get_worksheet_as_df]:
        func.clear_cache()


def merged_table(
    hierarchy_df,
    hierarchy_df_on,
    values_df,
    values_df_on,
    transformers={},
    drop_cols=[],
    rename_cols={},
):
    """Link a values table to its corresponding hierarchy table

    Arguments:
        hierarchy_df {DataFrame} -- DataFrame containing the tree structure of the entity
        hierarchy_df_on {str} -- The column on which the hierarchy DataFrame will occurr
        values_df {DataFrame} -- DataFrame containing the values for entries in the hierarchy DataFrame
        values_df_on {str} -- The column on which the values DataFrame will occurr
        transformers {dict} -- A mapping of column names and a list functions to be applied to said column after the merger occurs
        drop_cols {list} -- A list of column names to be dropped after the merger occurs
        rename_cols {dict} -- A mapping of existing column names and their replacement values, renaming
                              occurs after the merger occurs but before transformers are applied
    """

    # TODO transformers by dtype
    merged = (
        pd.merge(
            left=hierarchy_df,
            left_on=hierarchy_df_on,
            right=values_df,
            right_on=values_df_on,
        )
        .rename(columns=rename_cols)
        .drop(columns=drop_cols)
    )
    for col_name, transformer_list in transformers.items():
        for transformer in transformer_list:
            merged.loc[:, col_name] = merged.loc[:, col_name].apply(transformer)
            pass
    return merged

