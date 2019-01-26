import anytree
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

from utils import get_root, load_budget, to_tree

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    # "https://codepen.io/chriddyp/pen/bWLwgP.css",
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
budget = load_budget()
tree_root = get_root(to_tree(budget))
rendered_tree = str(anytree.RenderTree(tree_root).by_attr())


def get_organization_names(year=None):
    if year is None:
        return budget.organization_name.dropna().unique()
    else:
        year = int(year)
        return budget[budget.year == year].organization_name.dropna().unique()


def filter_budget(year=None, organization=None):
    if year is None or organization is None:
        return None
    return budget[
        (budget.year == int(year)) & (budget.organization_name == organization)
    ]


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

app.layout = dbc.Container(
    [
        html.H1("Validation budget"),
        filter_row,
        html.Pre(children=rendered_tree, id="pre"),
        dbc.Row(dbc.Col(datatable)),
    ]
)


@app.callback(
    Output(component_id="org-name", component_property="options"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_dropdown(year):
    return [{"label": val, "value": val} for val in get_organization_names(year)]


@app.callback(
    Output(component_id="pre", component_property="children"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="org-name", component_property="value"),
    ],
)
def update_pre(year, organization):
    return str(
        anytree.RenderTree(
            get_root(
                to_tree(
                    filter_budget(year=year, organization=organization)
                    .drop(columns=["year", "organization_name"])
                    .pipe(
                        lambda df: df.assign(
                            budget_type_parent_name=df[
                                "budget_type_parent_name"
                            ].fillna("ميزانية الوزارة")
                        )
                    )
                )
            )
        ).by_attr()
    )


@app.callback(
    Output(component_id="table", component_property="data"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="org-name", component_property="value"),
    ],
)
def update_datatable(year, organization):
    return (
        filter_budget(year, organization)
        .drop(columns=["year", "organization_name"])
        .pipe(
            lambda df: df.assign(
                budget_type_parent_name=df["budget_type_parent_name"].fillna(
                    "ميزانية الوزارة"
                )
            )
        )
        .to_dict("rows")
    )


if __name__ == "__main__":
    app.run_server(debug=True)
