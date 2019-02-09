from . import create_flask, create_dash
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

server = create_flask("../config.py")
app = create_dash(server)

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


with server.app_context():
    from . import callbacks

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
                        dbc.FormGroup(
                            [dbc.Label("Year", html_for="year"), year_dropdown]
                        )
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
                            [
                                dbc.Button(
                                    "Show table", id="collapse-button", color="info"
                                )
                            ]
                        )
                    ),
                ]
            ),
            dbc.Row([dbc.Col(dcc.Graph(id="graph"))]),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Collapse([dbc.Row(dbc.Col(datatable))], id="collapse"),
                        width=12,
                    )
                ]
            ),
        ]
    )

