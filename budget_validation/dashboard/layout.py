import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from budget_validation.utils import list_to_dropdown_options


# year_dropdown_options = [
#     {"label": val, "value": int(val)} for val in budget.year.unique()
# ]


def get_year_dropdown(years):
    years = list_to_dropdown_options(years)
    year_dropdown = dcc.Dropdown(
        id="year",
        options=years,
        value=years[0]["value"],
        placeholder="Year",
        clearable=False,
    )
    group = dbc.FormGroup(
        [
            dbc.Label("Year", html_for="year"),
            html.Div(id="year_dropdown_container", children=year_dropdown),
        ]
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
    group = dbc.FormGroup(
        [
            dbc.Label("Organization name", html_for="organization"),
            organization_name_dropdown,
        ]
    )

    return organization_name_dropdown


def get_datatable(df):
    datatable = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        sorting=True,
    )
    return datatable

