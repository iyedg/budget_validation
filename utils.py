import hashlib
import pandas as pd
from pathlib import Path
import numpy as np
import anytree


def hash_file(file_path):
    """
    Generate a hash digest for file
    """
    file_path = Path(file_path)
    hash_md5 = hashlib.md5()
    with open(str(file_path), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    digest = hash_md5.hexdigest()
    return digest


def to_parquet(data_dir):
    """
    Convert all csv files in the data directory to parquet
    in case they've changed from last run
    """
    data_dir = Path(data_dir)
    for csv in data_dir.glob("*.csv"):
        df = pd.read_csv(csv.absolute())
        parquet_path = Path(str(csv.absolute()).replace(csv.suffix, ".parquet"))
        df.to_parquet(parquet_path.absolute())
        print("{} is created".format(parquet_path))


def clean_currency(col):
    ill_formatted_numbers = col.apply(lambda val: "TND" not in str(val))
    col.loc[ill_formatted_numbers].apply(lambda val: val.replace(",", "."))
    return pd.to_numeric(col.str.replace("TND", "").str.replace(",", "")).apply(
        lambda val: np.round(val, 3)
    )


def load_budget():
    """
    Open, clean and return budget data frame
    """
    to_parquet("./data")

    budget_type = pd.read_parquet("data/saisie_db - budget_type.parquet")
    budget_by_type = pd.read_parquet("data/saisie_db - budget_by_type.parquet")

    budget = (
        pd.merge(
            left=budget_type,
            left_on="name",
            right=budget_by_type,
            right_on="budget_type_name",
        )
        .drop(
            columns=[
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
        )
        .rename(columns={"parent_name": "budget_type_parent_name"})
        .pipe(
            lambda df: df.assign(
                budget_type_parent_name=df["budget_type_parent_name"].str.strip()
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
    budget.to_parquet("data/budget.parquet")
    return budget


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
