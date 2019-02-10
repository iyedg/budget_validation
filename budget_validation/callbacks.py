import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

from budget_validation.loader import get_worksheet_as_df, merged_table
from budget_validation.tree import to_tree
from budget_validation.utils import clean_currency, list_to_dropdown_options

from .budget_validation import APP

BUDGET_TYPE = get_worksheet_as_df("budget_type")
BUDGET_BY_TYPE = get_worksheet_as_df("budget_by_type")

BUDGET = merged_table(
    hierarchy_df=BUDGET_TYPE,
    hierarchy_df_on="name",
    values_df=BUDGET_BY_TYPE,
    values_df_on="budget_type_name",
    transformers={
        "value": [clean_currency],
        "budget_type_parent_name": [lambda val: np.nan if val == "" else val.strip()],
        "budget_type_name": [lambda val: np.nan if val == "" else val.strip()],
    },
    drop_cols=[
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
    ],
    rename_cols={"parent_name": "budget_type_parent_name"},
)


@APP.callback(
    Output(component_id="organization", component_property="options"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_name_dropdown_options(year):
    return list_to_dropdown_options(
        BUDGET[BUDGET.year == year].organization_name.dropna().unique()
    )


@APP.callback(
    Output(component_id="organization", component_property="value"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_name_dropdown_value(year):
    return sorted(BUDGET[BUDGET.year == year].organization_name.dropna().unique())[0]


@APP.callback(
    Output(component_id="table", component_property="data"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="organization", component_property="value"),
    ],
)
def update_datatable(year, organization):
    filtered_budget = BUDGET[
        (BUDGET.year == year) & (BUDGET.organization_name == organization)
    ]
    if organization != "الدولة":
        filtered_budget = filtered_budget.pipe(
            lambda df: df.assign(
                budget_type_parent_name=df.budget_type_parent_name.fillna(
                    "ميزانية الوزارة"
                )
            )
        )
    return filtered_budget.sort_values(
        ["budget_type_parent_name", "value", "budget_type_name"], ascending=False
    ).to_dict("rows")


@APP.callback(
    Output(component_id="tree", component_property="elements"),
    [Input(component_id="table", component_property="data")],
)
def update_graph(df):
    df = pd.DataFrame(df)
    tree = to_tree(
        df, "budget_type_parent_name", "budget_type_name", "value", "ميزانية الوزارة"
    )
    return tree


@APP.callback(
    Output(component_id="duplicates", component_property="is_open"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="organization", component_property="value"),
    ],
)
def show_duplicates_error(year, organization):
    filtered_budget = BUDGET[
        (BUDGET.year == year) & (BUDGET.organization_name == organization)
    ]
    return filtered_budget.budget_type_name.duplicated().any()


@APP.callback(
    Output(component_id="duplicates", component_property="children"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="organization", component_property="value"),
    ],
)
def update_duplicates_error(year, organization):
    # TODO: any entry in the parent column must exist in the children column except for root
    filtered_budget = BUDGET[
        (BUDGET.year == year) & (BUDGET.organization_name == organization)
    ]
    return list(
        filtered_budget[filtered_budget.budget_type_name.duplicated()].budget_type_name
    )
