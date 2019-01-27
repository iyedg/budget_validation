import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from budget_validation.loader import load_budget

budget = load_budget()

organization_name_dropdown = dcc.Dropdown(
    id="org-name", placeholder="Organization name", clearable=False
)

year_dropdown_options = [
    {"label": val, "value": int(val)} for val in budget.year.unique()
]
year_dropdown = dcc.Dropdown(
    id="year",
    options=year_dropdown_options,
    value=year_dropdown_options[0]["value"],
    placeholder="Year",
    clearable=False,
)

filter_row = html.Div(
    dbc.Row(
        [
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("Organization name", html_for="org-name"),
                        organization_name_dropdown,
                    ]
                )
            ),
            dbc.Col(dbc.FormGroup([dbc.Label("Year", html_for="year"), year_dropdown])),
        ]
    )
)

datatable = dash_table.DataTable(
    id="table",
    columns=[
        {"name": i, "id": i}
        for i in budget.columns
        if i not in ["year", "organization_name"]
    ],
    data=budget.to_dict("rows"),
)

layout = dbc.Container(
    [
        html.H1("Validation budget"),
        filter_row,
        # html.Pre(children=rendered_tree, id="pre"),
        dbc.Row(dbc.Col(datatable)),
    ]
)
