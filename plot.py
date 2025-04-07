import matplotlib.pyplot as plt

def plot_tour(coords: dict, edges: list):
    """画出一条路径"""
    plt.figure(figsize=(8, 8))
    for (i, j) in edges:
        x = [coords[i][0], coords[j][0]]
        y = [coords[i][1], coords[j][1]]
        plt.plot(x, y, 'bo-')
    plt.scatter(*zip(*coords.values()), c='red')
    plt.axis('equal')
    plt.title("TSP Solution Tour")
    plt.show()