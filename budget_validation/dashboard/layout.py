import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from budget_validation.utils import list_to_dropdown_options


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
        style_table={"overflowX": "scroll"},
        style_header={"backgroundColor": "rgb(30, 30, 30)"},
        style_cell={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
        style_as_list_view=True,
    )
    return datatable

