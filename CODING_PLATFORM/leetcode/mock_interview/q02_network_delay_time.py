"""
There are N network nodes, labelled 1 to N.

Given times, a list of travel times as directed edges times[i] = (u, v, w), where u is the source node, v
is the target node, and w is the time it takes for a signal to travel from source to target.

Now, we send a signal from a certain node K. How long will it take for all nodes to receive the signal?
If it is impossible, return -1.

For example:
Input: times = [[2,1,1],[2,3,1],[3,4,1]], N = 4 (total numbers of nodes), K = 2 (starting node)
Output: 2

Note:
N will be in the range [1, 100].
K will be in the range [1, N].
The length of times will be in the range [1, 6000].
All edges times[i] = (u, v, w) will have 1 <= u, v <= N and 0 <= w <= 100.

"""
from collections import defaultdict
from typing import List


def networkDelayTime(times: List[List[int]], N: int, K: int) -> int:
    graph = defaultdict(list)
    INF = float('inf')
    for u, v, w in times:
        graph[u].append((v, w))  # for directed graph, only need to add one direction

    dist = {node: INF for node in range(1, N+1)}

    def dfs(node, d):
        if dist[node] <= d:
            return
        dist[node] = d
        for nei, time in graph[node]:
            dfs(nei, d + time)

    dfs(K, 0)
    res = max(dist.values())
    return -1 if res == INF else res


if __name__ == '__main__':
    times = [[2, 1, 1], [2, 3, 1], [3, 4, 2]]
    N = 4
    K = 2
    print(f'{networkDelayTime(times, N, K) = }')
