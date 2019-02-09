#%%
from budget_validation import tree
from budget_validation.loader import get_worksheet_as_df, merged_table
from budget_validation.utils import clean_currency, reshape
import pandas as pd
import numpy as np
import networkx as nx
from pprint import pprint

#%%
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


#%%
budget = get_budget_df()
budget15 = budget[budget.year == 2016]
b = budget15[budget15.organization_name == "وزارة التربية"].pipe(
    lambda df: df.assign(
        budget_type_parent_name=df.budget_type_parent_name.fillna("ميزانية الوزارة")
    )
)
b

#%%
t = tree.to_tree(
    b,
    parent_name_column="budget_type_parent_name",
    child_name_column="budget_type_name",
    child_value_column="value",
)

#%%

node_names = list(t.nodes)
reshaped_names = [reshape(n.decode("utf8")) for n in t.nodes]
mapping = dict(zip(node_names, reshaped_names))

#%%
rt = nx.relabel_nodes(t, mapping)

#%%
dfs_successors = nx.algorithms.traversal.dfs_successors(rt, "ﻣﻴﺰﺍﻧﻴﺔ ﺍﻟﻮﺯﺍﺭﺓ")
attrs = nx.get_node_attributes(rt, "value")

for node, children in dfs_successors.items():
    node_value = attrs.get(node)
    children_value = sum([attrs.get(child) for child in children])
    print(node)
    print("value:", node_value)
    print("children:", children_value)
    rt.nodes[node]["gap"] = node_value - children_value

pprint(nx.get_node_attributes(rt, "gap"))

#%%
tree.recursive_sum(t)


#%%
from budget_validation import tree
from budget_validation.loader import get_worksheet_as_df, merged_table
from budget_validation.utils import clean_currency, reshape
import pandas as pd
import numpy as np
import networkx as nx
from pprint import pprint
import missingno

budget_type = get_worksheet_as_df("budget_type")
budget_by_type = get_worksheet_as_df("budget_by_type")

t = merged_table(
    hierarchy_df=budget_type,
    hierarchy_df_on="name",
    values_df=budget_by_type,
    values_df_on="budget_type_name",
    transformers={
        "value": [clean_currency],
        "budget_type_parent_name": [lambda val: np.nan if val == "" else val.strip()],
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
