import networkx as nx
import matplotlib.pyplot as plt
from .utils import reshape
from .utils import fig_to_uri


def to_tree(df, parent_name_column, child_name_column, child_value_column):
    g = nx.Graph(directed=True)
    for row in df.to_dict("record"):
        child_name = row[child_name_column]
        child_value = row[child_value_column]
        parent_name = row[parent_name_column]
        g.add_node(reshape(child_name), value=child_value)
        g.add_edge(reshape(child_name), reshape(parent_name))
    return g


def draw_tree(df, *args, **kwargs):
    fig, ax = plt.subplots(1, 1)
    tree = to_tree(df, *args, **kwargs)
    nx.draw(tree, with_labels=True)
    return fig_to_uri(fig)
