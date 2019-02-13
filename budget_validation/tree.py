import pandas as pd
import numpy as np


def to_tree(
    df, parent_name_column, child_name_column, child_value_column, parent_name_fillna
):
    df.loc[:, parent_name_column] = df.loc[:, parent_name_column].fillna(
        parent_name_fillna
    )
    agg = df.groupby(parent_name_column).agg(sum)
    gap_records = (
        pd.merge(
            right=df, right_on=child_name_column, left=agg, left_on=parent_name_column
        )
        .pipe(
            lambda df: df.assign(
                gap=np.round(
                    df["{}_x".format(child_value_column)]
                    - df["{}_y".format(child_value_column)],
                    3,
                )
            )
        )
        .set_index("budget_type_parent_name")
        .to_dict("dict")
    )
    records = df.to_dict("records")
    nodes = []
    edges = []
    for record in records:
        child_name = record[child_name_column]
        parent_name = record[parent_name_column]
        child_value = record[child_value_column]
        nodes.append(
            {
                "data": {
                    "id": child_name,
                    "label": child_name,
                    "value": child_value,
                    "gap": gap_records.get("gap").get(parent_name),
                }
            }
        )
        edges.append({"data": {"source": parent_name, "target": child_name}})
    elements = nodes + edges
    return elements
