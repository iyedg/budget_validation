

def to_tree(
    df, parent_name_column, child_name_column, child_value_column, parent_name_fillna
):
    df.loc[:, parent_name_column] = df.loc[:, parent_name_column].fillna(
        parent_name_fillna
    )
    records = df.to_dict("records")
    nodes = []
    edges = []
    for record in records:
        child_name = record[child_name_column]
        parent_name = record[parent_name_column]
        child_value = record[child_value_column]
        nodes.append(
            {"data": {"id": child_name, "label": child_name, "value": child_value}}
        )
        edges.append({"data": {"source": parent_name, "target": child_name}})
    elements = nodes + edges
    return elements
