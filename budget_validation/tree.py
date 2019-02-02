import networkx as nx
from .utils import reshape
import plotly.graph_objs as go
import plotly.offline as py


def to_tree(df, parent_name_column, child_name_column, child_value_column):
    g = nx.Graph(directed=True)
    for row in df.to_dict("record"):
        child_name = row[child_name_column]
        child_value = row[child_value_column]
        parent_name = row[parent_name_column]
        g.add_node(reshape(child_name).encode("utf-8"), value=child_value)
        g.add_edge(
            reshape(child_name).encode("utf-8"), reshape(parent_name).encode("utf-8")
        )
    return g


def draw_tree(df, *args, **kwargs):
    tree = to_tree(df, *args, **kwargs)
    pos = nx.drawing.nx_pydot.pydot_layout(tree, "neato")
    node_values = [node[1].get("value") for node in tree.nodes.data()]
    node_names = [reshape(node[0].decode("utf8")) for node in tree.nodes.data()]
    x_nodes = [pos[i][0] for i in pos]
    y_nodes = [pos[i][1] for i in pos]
    x_edges = []
    y_edges = []
    for node1, node2 in tree.edges:
        node1_x, node1_y = pos[node1][0], pos[node1][1]
        node2_x, node2_y = pos[node2][0], pos[node2][1]
        x_edges.extend([node1_x, node2_x, None])
        y_edges.extend([node1_y, node2_y, None])
    trace_nodes = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        marker=dict(symbol="circle", size=18),
        text=node_names,
        hoverinfo="text",
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
    return fig

