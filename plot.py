"""
Warning:
This module is NOT finished. There may be some bugs!

Warning:
This module is NOT finished. There may be some bugs!

Warning:
This module is NOT finished. There may be some bugs!

Warning:
This module is NOT finished. There may be some bugs!
"""

import matplotlib.pyplot as plt

def is_feasible_tsp(edges: list, tspBuffer=1) -> bool:
    """
    判断当前路径是否是一个可行的旅行商解。
    条件：每个节点入度 = 出度 = 1，且形成一个封闭环。
    """
    from collections import defaultdict

    out_deg = defaultdict(int)
    in_deg = defaultdict(int)
    node_set = set()
    next_map = {}

    for (tmpi, tmpj) in edges:
        i = tmpi + tspBuffer
        j = tmpj + tspBuffer
        out_deg[i] += 1
        in_deg[j] += 1
        node_set.update([i, j])
        if i in next_map:
            print(f"Node {i} has more than one outgoing edge!")
            return False
        next_map[i] = j

    # 每个点出度和入度都要为1
    for node in node_set:
        if out_deg[node] + in_deg[node] != 2:
            print(f"Node {node} in + out degree is not 2")
            return False

    # 检查是否连通并形成一个回路
    visited = set()
    start = next(iter(node_set))
    current = start

    for _ in range(len(node_set)):
        if current in visited:
            print("Cycle revisited node before finishing")
            return False
        visited.add(current)
        if current not in next_map:
            print(f"Node {current} has no outgoing edge")
            return False
        current = next_map[current]

    return current == start and len(visited) == len(node_set)



def plot_tour(coords: dict, edges: list, tspBuffer=1):
    """画出一条路径，同时检查是否为TSP可行解"""
    feasible = is_feasible_tsp(edges, tspBuffer)
    print("is feasible?", "Y" if feasible else "N")

    plt.figure(figsize=(8, 8))
    for (tmpi, tmpj) in edges:
        i = tmpi + tspBuffer
        j = tmpj + tspBuffer
        x = [coords[i][0], coords[j][0]]
        y = [coords[i][1], coords[j][1]]
        plt.plot(x, y, 'bo-')
    plt.scatter(*zip(*coords.values()), c='red')
    plt.axis('equal')
    plt.title("TSP Solution Tour")
    plt.show()
