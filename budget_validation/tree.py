import networkx as nx
import numpy as np
import plotly.graph_objs as go

from .utils import reshape


def to_tree(df, parent_name_column, child_name_column, child_value_column):
    g = nx.DiGraph()
    for row in df.to_dict("record"):
        child_name = row[child_name_column]
        child_value = row[child_value_column]
        parent_name = row[parent_name_column]
        g.add_node(reshape(child_name).encode("utf-8"), value=child_value)
        g.add_edge(
            reshape(parent_name).encode("utf-8"), reshape(child_name).encode("utf-8")
        )
    return g


def recursive_sum(tree):
    """
    Recursively calculate the sum of each node's children, and add a gap attribute
     for the difference between the sum of the children's value and the node's value.

    Arguments:
        tree {networkx.DiGraph} -- a tree generated by `to_tree`

    """
    node_names = list(tree.nodes)
    reshaped_names = [reshape(n.decode("utf8")) for n in tree.nodes]
    mapping = dict(zip(node_names, reshaped_names))
    tree = nx.relabel_nodes(tree, mapping)
    # TODO: only works for ministries, must work for state
    dfs_successors = nx.algorithms.traversal.dfs_successors(tree, "ﻣﻴﺰﺍﻧﻴﺔ ﺍﻟﻮﺯﺍﺭﺓ")
    attrs = nx.get_node_attributes(tree, "value")
    for node, children in dfs_successors.items():
        node_value = np.round(attrs.get(node), 3)
        children_value = np.round(sum([attrs.get(child) for child in children]), 3)
        tree.nodes[node]["gap"] = np.round(node_value - children_value, 3)

    return tree


def draw_tree(df, *args, **kwargs):
    tree = to_tree(df, *args, **kwargs)
    pos = nx.drawing.nx_pydot.pydot_layout(tree, "dot")
    # TODO: Handle Unicode issue with NetworkX for the function reshape
    node_names = [reshape(node.decode("utf8")) for node in tree.nodes]
    x_nodes = [pos[i][0] for i in pos]
    y_nodes = [pos[i][1] for i in pos]
    x_edges = []
    y_edges = []
    for node1, node2 in tree.edges:
        node1_x, node1_y = pos[node1][0], pos[node1][1]
        node2_x, node2_y = pos[node2][0], pos[node2][1]
        x_edges.extend([node2_x, node1_x, None])
        y_edges.extend([node2_y, node1_y, None])
    trace_nodes = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        marker=dict(symbol="circle", size=25),
        text=node_names,
    )
    trace_edges = go.Scatter(x=x_edges, y=y_edges, mode="lines", hoverinfo="none")
    axis = dict(
        showline=False,  # hide axis line, grid, ticklabels and  title
        zeroline=False,
        showgrid=False,
        showticklabels=False,
    )
    layout = go.Layout(
        showlegend=False,
        xaxis=go.layout.XAxis(axis),
        yaxis=go.layout.YAxis(axis),
        hovermode="closest",
    )
    fig = go.Figure(data=[trace_edges, trace_nodes], layout=layout)
    fig.layout.template = "plotly_white"
    return fig
