import anytree
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

from budget_validation.dashboard.layout import (
    get_datatable,
    get_organization_name_dropdown,
    get_year_dropdown,
)
from budget_validation.loader import get_worksheet_as_df
from budget_validation.tree import draw_tree
from budget_validation.utils import clean_currency, list_to_dropdown_options


def get_budget_df():
    """
    Return a dataframe for budget validation
    TODO: improve API, make it DRY and general
    """

    drop_cols = [
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
    budget_type = get_worksheet_as_df("budget_type")
    budget_by_type = get_worksheet_as_df("budget_by_type")
    budget = (
        pd.merge(
            left=budget_type,
            left_on="name",
            right=budget_by_type,
            right_on="budget_type_name",
        )
        .drop(columns=drop_cols)
        .rename(columns={"parent_name": "budget_type_parent_name"})
        .pipe(
            lambda df: df.assign(
                budget_type_parent_name=df["budget_type_parent_name"]
                .str.strip()
                .replace("", np.nan)
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


budget = get_budget_df()

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

year_dropdown = get_year_dropdown(budget.year.unique())
app.layout = dbc.Container(
    [
        html.H1("Budget validation"),
        dbc.Row(
            [
                dbc.Col(year_dropdown),
                dbc.Col(
                    get_organization_name_dropdown(
                        budget[budget.year == 2015].organization_name.dropna().unique()
                    )
                ),
            ]
        ),
        dbc.Row(dbc.Col(get_datatable(budget[budget.year == 2015]))),
        dbc.Row(dbc.Col(html.Img(id="graph", src="assets/graph.png", alt="Graph"))),
    ],
    fluid=True,
)


@app.callback(
    Output(component_id="organization", component_property="options"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_name_dropdown_options(year):
    return list_to_dropdown_options(
        budget[budget.year == year].organization_name.dropna().unique()
    )


@app.callback(
    Output(component_id="organization", component_property="value"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_name_dropdown_value(year):
    return sorted(budget[budget.year == year].organization_name.dropna().unique())[0]


@app.callback(
    Output(component_id="table", component_property="data"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="organization", component_property="value"),
    ],
)
def update_datatable(year, organization):
    filtered_budget = budget[
        (budget.year == year) & (budget.organization_name == organization)
    ]
    if organization != "الدولة":
        filtered_budget = filtered_budget.pipe(
            lambda df: df.assign(
                budget_type_parent_name=df.budget_type_parent_name.fillna(
                    "ميزانية الوزارة"
                )
            )
        )
    return filtered_budget.to_dict("rows")


@app.callback(
    Output(component_id="graph", component_property="src"),
    [Input(component_id="table", component_property="data")],
)
def update_graph(df):
    df = pd.DataFrame(df)
    return draw_tree(
        df,
        parent_name_column="budget_type_parent_name",
        child_name_column="budget_type_name",
        child_value_column="value",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
