import anytree
import dash
from dash.dependencies import Input, Output

from budget_validation.loader import load_budget
from budget_validation.utils import get_root, to_tree
from budget_validation.dashboard.layout import layout

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = layout


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


@app.callback(
    Output(component_id="org-name", component_property="options"),
    [Input(component_id="year", component_property="value")],
)
def update_organization_dropdown(year):
    return [{"label": val, "value": val} for val in get_organization_names(year)]


@app.callback(
    Output(component_id="org-name", component_property="value"),
    [Input(component_id="org-name", component_property="options")],
)
def update_organization_dropdown_value(options):
    return options[0]


# @app.callback(
#     Output(component_id="pre", component_property="children"),
#     [
#         Input(component_id="year", component_property="value"),
#         Input(component_id="org-name", component_property="value"),
#     ],
# )
# def update_pre(year, organization):
#     return str(
#         anytree.RenderTree(
#             get_root(
#                 to_tree(
#                     filter_budget(year=year, organization=organization)
#                     .drop(columns=["year", "organization_name"])
#                     .pipe(
#                         lambda df: df.assign(
#                             budget_type_parent_name=df[
#                                 "budget_type_parent_name"
#                             ].fillna("ميزانية الوزارة")
#                         )
#                     )
#                 )
#             )
#         ).by_attr()
#     )


@app.callback(
    Output(component_id="table", component_property="data"),
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="org-name", component_property="value"),
    ],
)
def update_datatable(year, organization):

    df = (
        filter_budget(year, organization)
        .drop(columns=["year", "organization_name"])
        .pipe(
            lambda df: df.assign(
                budget_type_parent_name=df["budget_type_parent_name"].fillna(
                    "ميزانية الوزارة"
                )
            )
        )
    )
    return df.to_dict("rows")


if __name__ == "__main__":
    app.run_server(debug=True)
