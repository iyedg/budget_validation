# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
from pprint import pprint

import pygraphviz as pgv
from anytree import AsciiStyle, Node, PreOrderIter, RenderTree
from IPython.display import Image

from utils import load_budget

# %%
budget = load_budget()
budget.head()

# %%
budget19 = budget[budget.year == 2019]
t = budget19[budget19.organization_name == "وزارة النقل"].pipe(
    lambda df: df.assign(
        budget_type_parent_name=df["budget_type_parent_name"].fillna("ميزانية الوزارة")
    )
)

# %%
tree = to_tree(t)
root = tree.popitem()[1].root

# %%
for node in root.descendants:
    if len(node.children) > 0:
        node.gap = np.round(node.value - sum([c.value for c in node.children]), 3)

# %%
print(RenderTree(root, style=AsciiStyle()))


# %%
g = pgv.AGraph(strict=False, directed=True)

# %%
for node in PreOrderIter(root):
    if node.is_root:
        g.add_node(node.name)
    else:
        g.add_edge(node.parent.name, node.name)

# %%
g.layout("dot")
g.draw("./draw.png")
Image(filename="./draw.png")

# %%

