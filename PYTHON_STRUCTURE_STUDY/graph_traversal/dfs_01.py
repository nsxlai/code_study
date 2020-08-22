# source: https://www.programiz.com/dsa/graph-dfs
# DFS algorithm in Python


# DFS algorithm
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)

    print(start)

    for next in graph[start] - visited:
        dfs(graph, next, visited)
    return visited


if __name__ == '__main__':
    graph = {'0': {'1', '2'},
             '1': {'0', '3', '4'},
             '2': {'0'},
             '3': {'1'},
             '4': {'2', '3'}}

    dfs(graph, '0')
