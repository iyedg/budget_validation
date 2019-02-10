import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import dash_table
import numpy as np

from budget_validation.loader import get_worksheet_as_df, merged_table
from budget_validation.utils import list_to_dropdown_options

from .utils import clean_currency


def get_year_dropdown(years):
    years = list_to_dropdown_options(years)
    year_dropdown = dcc.Dropdown(
        id="year",
        options=years,
        value=years[0]["value"],
        placeholder="Year",
        clearable=False,
    )
    return year_dropdown


def get_organization_name_dropdown(organization_names):
    organization_names = list_to_dropdown_options(organization_names)
    organization_name_dropdown = dcc.Dropdown(
        id="organization",
        placeholder="Organization name",
        clearable=False,
        options=organization_names,
        value=organization_names[0],
    )

    return organization_name_dropdown


def get_datatable(df):
    datatable = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        style_header={"fontFamily": "inherit"},
    )
    return datatable


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


year_dropdown = get_year_dropdown(budget.year.unique())
organization_name_dropdown = get_organization_name_dropdown(
    budget[budget.year == year_dropdown.value].organization_name.dropna().unique()
)
datatable = get_datatable(
    budget[budget.year == year_dropdown.value].drop(
        columns=["extra", "year", "organization_name"]
    )
)
layout = dbc.Container(
    [
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
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    cyto.Cytoscape(
                        id="tree",
                        layout={
                            "name": "breadthfirst",
                            "roots": "[id='ميزانية الوزارة']",
                        },
                        style={"width": "100%", "height": "400px"},
                        elements=[],
                    )
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Alert(
                                        "This table contains duplicate entries",
                                        color="danger",
                                        fade=True,
                                        is_open=False,
                                        id="duplicates",
                                    ),
                                    width=12,
                                ),
                                dbc.Col(datatable),
                            ]
                        )
                    ]
                ),
            ]
        ),
    ]
)
