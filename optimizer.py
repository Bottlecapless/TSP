import gurobipy as gp
from gurobipy import GRB
import coptpy as cp
from coptpy import COPT
from itertools import combinations
from collections import defaultdict

from TSPProblem import TSPProblem

class TSPCallback:
    def __init__(self, nodes, x):
        self.nodes = nodes
        self.x = x

    def __call__(self, model, where):
        if where == GRB.Callback.MIPSOL:
            try:
                values = model.cbGetSolution(self.x)
                edges = [(i, j) for (i, j), v in values.items() if v > 0.5]
                tour = self._shortest_subtour(edges)
                if len(tour) < len(self.nodes):
                    model.cbLazy(
                        gp.quicksum(self.x[i, j] for i, j in combinations(tour, 2))
                        <= len(tour) - 1
                    )
            except Exception as e:
                print("Callback failed:", e)
                model.terminate()

    def _shortest_subtour(self, edges):
        # 寻找当前最短的环（非全图）
        neighbors = defaultdict(list)
        for i, j in edges:
            neighbors[i].append(j)
            neighbors[j].append(i)  # 对称图

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


class Optimizer:
    def __init__(self, tsp_problem:TSPProblem, timeLimit=120):
        self.tsp_problem = tsp_problem
        self.n = tsp_problem.dimension
        self.distances = tsp_problem.distances
        self.model = None
        self.timeLimit = timeLimit

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

            # 添加约束：每个点度数为2
            for i in nodes:
                model.addConstr(gp.quicksum(x[min(i, j), max(i, j)] for j in nodes if i != j) == 2)

            # 设置参数
            model.setParam('TimeLimit', self.timeLimit)
            model.setParam("MIPFocus", 1)
            model.setParam("ImproveStartTime", 5)
            model.setParam("ImproveStartNodes", 100)
            model.setParam("Cuts", 1)
            model.setParam("Heuristics", 0.5)
            model.setParam("Presolve", 1)
            model.setParam("Threads", 8)

            # 优化模型（带 callback）
            cb = TSPCallback(nodes, x)
            model.optimize(cb)

            # 解析解
            if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
                vals = model.getAttr("X", x)
                edges_used = [(i, j) for (i, j), val in vals.items() if val > 0.5]
                return {
                    "solver": "Gurobi",
                    "status": "Optimal" if model.status == GRB.OPTIMAL else "Time Limit",
                    "edges": edges_used,
                    "objective": model.ObjVal,
                    "gap": model.MIPGap,
                    "time": model.Runtime
                }
            else:
                return {"solver": "Gurobi", "status": "Failed"}

        except gp.GurobiError as e:
            return {"solver": "Gurobi", "status": f"Error: {str(e)}"}

        
    # def solve_with_copt(self):
    #     try:
    #         env = cp.Envr()
    #         model = env.createModel(name="TSP_COPT")  # 正确方式创建模型
    #         self.model = model

    #         n = self.n
    #         distances = self.distances
    #         x = {}

    #         # 创建二进制变量 x[i,j]
    #         for i in range(n):
    #             for j in range(n):
    #                 if i != j:
    #                     x[i, j] = model.addVar(vtype=COPT.BINARY, name=f"x_{i}_{j}")
    #         self.x = x

    #         # 每个城市只能进入一次
    #         for j in range(n):
    #             model.addConstr(cp.quicksum(x[i, j] for i in range(n) if i != j) == 1)

    #         # 每个城市只能离开一次
    #         for i in range(n):
    #             model.addConstr(cp.quicksum(x[i, j] for j in range(n) if i != j) == 1)

    #         # 使用MTZ消除子回路，添加辅助变量 u[i]
    #         u = {}
    #         for i in range(1, n):
    #             u[i] = model.addVar(lb=0, ub=n - 1, vtype=COPT.INTEGER, name=f"u_{i}")
    #         self.u = u

    #         for i in range(1, n):
    #             for j in range(1, n):
    #                 if i != j:
    #                     model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)

    #         # 设置目标函数：最小化总旅行距离
    #         model.setObjective(
    #             cp.quicksum(distances[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j),
    #             sense=cp.COPT.MINIMIZE
    #         )

    #         # 设置参数（注意是字符串）
    #         model.setParam("TimeLimit", self.timeLimit)
            

    #         model.solve()

    #         status = model.getAttr("Status")
    #         if status in [cp.COPT.OPTIMAL, cp.COPT.TIMEOUT]:
    #             lb = model.getAttr("BestBd")
    #             obj_value = model.getAttr("ObjVal")
    #             mip_gap = model.getAttr("MIPGap")
    #             runtime = model.getAttr("Runtime")
    #             status_str = "Optimal" if status == cp.COPT.OPTIMAL else "Time Limit"

    #             return {
    #                 "solver": "COPT",
    #                 "status": status_str,
    #                 "lb": lb,
    #                 "objective": obj_value,
    #                 "gap": mip_gap,
    #                 "time": runtime
    #             }
    #         else:
    #             return {
    #                 "solver": "COPT",
    #                 "status": "Failed"
    #             }

    #     except cp.CoptError as e:
    #         return {
    #             "solver": "COPT",
    #             "status": f"Error: {str(e)}"
    #         }
