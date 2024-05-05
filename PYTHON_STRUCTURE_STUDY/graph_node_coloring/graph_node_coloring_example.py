"""
source: https://www.youtube.com/watch?v=AyrrZ4PCyws&t=3s

Need to install the matplotlib and networkx Python library
"""
import random
import itertools
import networkx as nx
import matplotlib.pyplot as plt


def is_valid_coloring(graph: nx.classes.graph.Graph, coloring):
    for u, v, in graph.edges():
        if coloring[u] == coloring[v]:
            return False
    return True


def greedy_coloring(graph: nx.classes.graph.Graph):
    coloring = {}
    for node in graph.nodes():
        adjacent_colors = {coloring.get(neighbor) for neighbor in graph.neighbors(node)}
        coloring[node] = next(color for color in itertools.count() if color not in adjacent_colors)
    return coloring


if __name__ == '__main__':

    n_nodes = 25

    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))

    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if random.random() < 0.1:
                G.add_edge(i, j)

    coloring_result = greedy_coloring(G)

    print(f'{coloring_result = }')
    print(f'Valid: {is_valid_coloring(G, coloring_result)}')
    print(f'K: {len(set(coloring_result.values()))}')

    color_map = [coloring_result[node] for node in G.nodes()]
    nx.draw(G, node_color=color_map, with_labels=True, font_weight='bold')
    plt.show()
