import gurobipy as gp
from gurobipy import GRB
import coptpy as cp
from coptpy import COPT
from itertools import combinations
from collections import defaultdict

from TSPProblem import TSPProblem
from plot import plot_tour

class TSPCallback:
    """
    Lazy constraint-based formulation solves the TSP as a compact 
    degree-constrained integer program and incrementally adds 
    subtour elimination constraints only when necessary. This 
    leads to a much smaller initial model and allows the solver 
    to focus on promising regions of the solution space early on. 
    Mathematically, this approach follows the branch-and-cut 
    paradigm, which is both computationally efficient and 
    robust against model scaling.
    """
    def __init__(self, nodes, x):
        self.nodes = nodes
        self.x = x

    def __call__(self, model, where):
        if where == GRB.Callback.MIPSOL:
            try:
                values = model.cbGetSolution(self.x)
                edges = [(i, j) for (i, j), v in values.items() if v > 0.5]
                tour = self._shortest_subtour(edges)

                # 只有找到合法子环，才添加 lazy constraint
                if len(tour) < len(self.nodes):
                    model.cbLazy(
                        gp.quicksum(self.x[min(i, j), max(i, j)] for i, j in combinations(tour, 2))
                        <= len(tour) - 1
                    )

            except ValueError as ve:
                # 跳过非法结构，不终止求解
                print("Skipping invalid solution in callback:", ve)

            except Exception as e:
                # 其他异常终止模型，便于调试
                print("Callback failed with unexpected error:", e)
                model.terminate()

    def _shortest_subtour(self, edges):
        neighbors = defaultdict(list)
        for i, j in edges:
            neighbors[i].append(j)
            neighbors[j].append(i)  # 对称图

        # 容错：跳过非法结构
        if not all(len(neighbors[i]) == 2 for i in neighbors):
            raise ValueError("Invalid tour structure in callback!")

        visited = set()
        shortest = None

        for start in neighbors:
            if start in visited:
                continue
            this_tour = [start]
            visited.add(start)
            next_node = neighbors[start][0]
            while next_node != start:
                this_tour.append(next_node)
                visited.add(next_node)
                next_candidates = [n for n in neighbors[next_node] if n not in visited]
                if not next_candidates:
                    break
                next_node = next_candidates[0]
            if shortest is None or len(this_tour) < len(shortest):
                shortest = this_tour
        return shortest



class GRB_Optimizer:
    def __init__(self, tsp_problem:TSPProblem, timeLimit=120):
        self.tsp_problem = tsp_problem
        self.n = tsp_problem.dimension
        self.distances = tsp_problem.distances
        self.model = None
        self.timeLimit = timeLimit

    def _generate_nearest_neighbor_tour(self):
        """使用最近邻算法生成一条初始可行路径（返回边列表）"""
        n = self.n
        coords = self.tsp_problem.coordinates
        unvisited = set(range(n))
        tour = []
        current = 0
        unvisited.remove(current)

        while unvisited:
            nearest = min(unvisited, key=lambda j: self.distances[current][j])
            tour.append((min(current, nearest), max(current, nearest)))
            current = nearest
            unvisited.remove(current)

        # 回到起点
        tour.append((min(current, 0), max(current, 0)))
        return tour


    def solve_with_lazy_gurobi(self):
        try:
            model = gp.Model("TSP_Lazy")
            model.Params.LazyConstraints = 1

            n = self.n
            nodes = list(range(n))
            dist = self.distances

            dist_dict = self.tsp_problem.get_distance_dict()
            edges = list(dist_dict.keys())
            x = model.addVars(edges, obj=dist_dict, vtype=GRB.BINARY, name="x")

            # 设置初始解（最近邻法）
            init_tour = self._generate_nearest_neighbor_tour()
            for i, j in init_tour:
                x[i, j].start = 1

            # 添加约束：每个点度数为2
            # for i in nodes:
            #     model.addConstr(gp.quicksum(x[min(i, j), max(i, j)] for j in nodes if i != j) == 2)
            for i in nodes:
                model.addConstr(
                    gp.quicksum(x[i, j] if i < j else x[j, i] for j in nodes if i != j) == 2
                )

            # 设置参数
            model.setParam('TimeLimit', self.timeLimit)
            model.setParam("MIPFocus", 1)
            model.setParam("ImproveStartTime", 5)
            model.setParam("ImproveStartNodes", 100)
            model.setParam("Cuts", 1)
            model.setParam("Heuristics", 0.8)
            model.setParam("Presolve", 1)
            model.setParam("Threads", 8)
            model.setParam("MIPGap", 0.000001)

            # 优化模型（带 callback）
            cb = TSPCallback(nodes, x)
            model.optimize(cb)

            # 解析解
            if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
                vals = model.getAttr("X", x)
                edges_used = [(i, j) for (i, j), val in vals.items() if val > 0.5]
                self.use_feasible_check(edges_used)
                return {
                    "solver": "Gurobi",
                    "status": "Optimal" if model.status == GRB.OPTIMAL else "Time Limit",
                    "lb": model.ObjBound,
                    "objective": model.ObjVal,
                    "gap": model.MIPGap,
                    "time": model.Runtime,
                    "edges": edges_used
                }
            else:
                return {"solver": "Gurobi", "status": "Failed"}

        except gp.GurobiError as e:
            return {"solver": "Gurobi", "status": f"Error: {str(e)}"}
        
    def use_feasible_check(self, edges):
        coords = self.tsp_problem.coordinates
        plot_tour(coords, edges)