"""
source: https://www.youtube.com/watch?v=7XVTnCrWDPY&t=440s

NeuralNine: Graph Search Visualization in Python (BFS and DFS)
"""
import queue
import networkx as nx
import matplotlib.pyplot as plt
import time


def order_bfs(graph, start_node):
    visited = set()
    q = queue.Queue()
    q.put(start_node)
    order = []

    while not q.empty():
        vertex = q.get()
        if vertex not in visited:
            order.append(vertex)
            visited.add(vertex)
            for node in graph[vertex]:
                if node not in visited:
                    q.put(node)

    return order


def order_dfs(graph, start_node, visited):
    if visited is None:
        visited = set()

    order = []

    if start_node not in visited:
        order.append(start_node)
        visited.add(start_node)
        for node in graph[start_node]:
            if node not in visited:
                order.extend(order_dfs(graph, node, visited))

    return order


def visualize_search(order, title, G, pos):
    plt.figure()
    plt.title(title)
    for i, node in enumerate(order, start=1):
        plt.clf()
        plt.title(title)
        nx.draw(G, pos, with_labels=True, node_color=['r' if n == node else 'g' for n in G.nodes])
        plt.draw()
        plt.pause(0.5)
    plt.show()
    time.sleep(0.5)


def generate_connected_random_graph(n, m):
    """
    This function will generate random graph with n nodes and m edges
    """
    while True:
        G = nx.gnm_random_graph(n, m)
        if nx.is_connected(G):
            return G


def user_defined_graph():
    """
    This function will show both BFS and DFS visualization. After the BFS graph progression is done, close the
    program and the DFS graph will pop up and start running
    """
    G = nx.Graph()
    G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('B', 'E'), ('C', 'F'), ('C', 'G')])
    pos = nx.spring_layout(G)

    visualize_search(order_bfs(G, start_node='A'), 'BFS Visualization', G, pos)
    visualize_search(order_dfs(G, start_node='A', visited=None), 'DFS Visualization', G, pos)


def auto_generated_graph():
    G = generate_connected_random_graph(10, 15)
    pos = nx.spring_layout(G)

    visualize_search(order_bfs(G, start_node=0), 'BFS Visualization', G, pos)  # random generated graph starts at 0
    visualize_search(order_dfs(G, start_node=0, visited=None), 'DFS Visualization', G, pos)


if __name__ == '__main__':
    user_defined_graph()
    auto_generated_graph()
