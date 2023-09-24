# source: https://www.programiz.com/dsa/graph-dfs
# DFS algorithm in Python


# DFS algorithm
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)

    print(start)

    stack = graph[start] - visited
    for nx in stack:
        if nx not in visited:
            dfs(graph, nx, visited)
    return visited


if __name__ == '__main__':
    graph1 = {'0': {'1', '2'},
              '1': {'0', '3', '4'},
              '2': {'0'},
              '3': {'1'},
              '4': {'2', '3'}}

    graph2 = {'0': {'1', '2', '3'},
              '1': {'0', '2'},
              '2': {'0', '1', '4'},
              '3': {'0'},
              '4': {'2'}}

    print('DFS on graph1')
    dfs(graph1, '0')

    print('DFS on graph2')
    dfs(graph2, '0')
