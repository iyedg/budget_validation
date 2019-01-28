import pandas as pd
import numpy as np
import anytree


def clean_currency(col):
    ill_formatted_numbers = col.apply(lambda val: "TND" not in str(val))
    col.loc[ill_formatted_numbers].apply(lambda val: val.replace(",", "."))
    return pd.to_numeric(col.str.replace("TND", "").str.replace(",", "")).apply(
        lambda val: np.round(val, 3)
    )


def to_tree(df):
    nodes = {}
    for record in df.to_dict("records"):
        child = record["budget_type_name"]
        parent = record["budget_type_parent_name"]
        # Parent has not been created yet
        if nodes.get(parent) is None:
            nodes[parent] = anytree.Node(parent)
        parent = nodes.get(parent)

        # Child already exists
        if nodes.get(child) is not None:
            child = nodes.get(child)
            child.parent = parent
            child.value = record["value"]
        else:
            nodes[child] = anytree.Node(child, parent=parent, value=record["value"])
    return nodes


def get_root(tree_dict):
    root = tree_dict.popitem()[1].root
    return root


def list_to_dropdown_options(lst):
    return sorted(
        [{"label": val, "value": val} for val in lst], key=lambda i: i["value"]
    )
