import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State

from budget_validation.dashboard.layout import (
    get_datatable,
    get_organization_name_dropdown,
    get_year_dropdown,
)
from budget_validation.loader import get_worksheet_as_df, merged_table
from budget_validation.tree import draw_tree
from budget_validation.utils import clean_currency, list_to_dropdown_options


budget_type = get_worksheet_as_df("budget_type")
budget_by_type = get_worksheet_as_df("budget_by_type")

budget = merged_table(
    hierarchy_df=budget_type,
    hierarchy_df_on="name",
    values_df=budget_by_type,
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


app = dash.Dash(__name__)
app.css.append_css({"external_url": "https://codepen.io/iyedg/pen/gqRLLM.css"})
app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True

year_dropdown = get_year_dropdown(budget.year.unique())
organization_name_dropdown = get_organization_name_dropdown(
    budget[budget.year == year_dropdown.value].organization_name.dropna().unique()
)
datatable = get_datatable(
    budget[budget.year == year_dropdown.value].drop(
        columns=["extra", "year", "organization_name"]
    )
)
app.layout = dbc.Container(
    [
        dcc.Interval(id="refresh", interval=200),
        html.H1("Budget validation"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.FormGroup([dbc.Label("Year", html_for="year"), year_dropdown])
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Organization name", html_for="organization"),
                            organization_name_dropdown,
                        ]
                    )
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [dbc.Button("Show table", id="collapse-button", color="info")]
                    )
                ),
            ]
        ),
        dbc.Row([dbc.Col(dcc.Graph(id="graph"))]),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Collapse([dbc.Row(dbc.Col(datatable))], id="collapse"), width=12
                )
            ]
        ),
    ]
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


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
    return filtered_budget.sort_values("value", ascending=False).to_dict("rows")


@app.callback(
    Output(component_id="graph", component_property="figure"),
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
