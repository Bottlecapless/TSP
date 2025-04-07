import gurobipy as gp
from gurobipy import GRB

import coptpy as cp
from coptpy import COPT

from TSPProblem import TSPProblem

class Optimizer:
    def __init__(self, tsp_problem, timeLimit = 120):
        self.tsp_problem = tsp_problem
        self.n = tsp_problem.dimension
        self.distances = tsp_problem.distances
        self.x = {}
        self.u = {}
        self.model = None
        self.timeLimit = timeLimit

    # 使用Gurobi求解TSP问题
    def solve_with_gurobi(self):
        tsp_problem = self.tsp_problem
        try:
            # 创建模型
            model = gp.Model("TSP_Gurobi")
            
            n = tsp_problem.dimension
            distances = tsp_problem.distances
            
            # 创建变量
            x = {}
            for i in range(n):
                for j in range(n):
                    if i != j:
                        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')
            
            # 添加约束：每个城市只能进入一次
            for j in range(n):
                model.addConstr(gp.quicksum(x[i, j] for i in range(n) if i != j) == 1)
            
            # 添加约束：每个城市只能离开一次
            for i in range(n):
                model.addConstr(gp.quicksum(x[i, j] for j in range(n) if i != j) == 1)
            
            # 消除子回路约束（使用MTZ公式）
            u = {}
            for i in range(1, n):
                u[i] = model.addVar(lb=0, ub=n-1, vtype=GRB.INTEGER, name=f'u_{i}')
            
            for i in range(1, n):
                for j in range(1, n):
                    if i != j:
                        model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)
            
            # 设置目标函数
            model.setObjective(gp.quicksum(distances[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j), GRB.MINIMIZE)
            
            model.setParam('TimeLimit', self.timeLimit)
            model.setParam("MIPFocus", 1)  # 强调寻找可行解
            
            # 求解模型
            model.optimize()
            
            if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
                lb = model.ObjBound
                obj_value = model.ObjVal
                gap = model.MIPGap
                status = "Optimal" if model.status == GRB.OPTIMAL else "Time Limit"
                runTime = model.Runtime
                
                return {
                    "solver": "Gurobi",
                    "status": status,
                    "lb": lb,
                    "objective": obj_value,
                    "gap": gap,
                    "time": runTime
                }
            else:
                return {
                    "solver": "Gurobi",
                    "status": "Failed",
                }
        
        except gp.GurobiError as e:
            return {
                "solver": "Gurobi",
                "status": f"Error: {str(e)}",
            }
        
    def solve_with_copt(self):
        try:
            env = cp.Envr()
            model = env.createModel(name="TSP_COPT")  # 正确方式创建模型
            self.model = model

            n = self.n
            distances = self.distances
            x = {}

            # 创建二进制变量 x[i,j]
            for i in range(n):
                for j in range(n):
                    if i != j:
                        x[i, j] = model.addVar(vtype=COPT.BINARY, name=f"x_{i}_{j}")
            self.x = x

            # 每个城市只能进入一次
            for j in range(n):
                model.addConstr(cp.quicksum(x[i, j] for i in range(n) if i != j) == 1)

            # 每个城市只能离开一次
            for i in range(n):
                model.addConstr(cp.quicksum(x[i, j] for j in range(n) if i != j) == 1)

            # 使用MTZ消除子回路，添加辅助变量 u[i]
            u = {}
            for i in range(1, n):
                u[i] = model.addVar(lb=0, ub=n - 1, vtype=COPT.INTEGER, name=f"u_{i}")
            self.u = u

            for i in range(1, n):
                for j in range(1, n):
                    if i != j:
                        model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)

            # 设置目标函数：最小化总旅行距离
            model.setObjective(
                cp.quicksum(distances[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j),
                sense=cp.COPT.MINIMIZE
            )

            # 设置参数（注意是字符串）
            model.setParam("TimeLimit", self.timeLimit)

            model.solve()

            status = model.getAttr("Status")
            if status in [cp.COPT.OPTIMAL, cp.COPT.TIMEOUT]:
                lb = model.getAttr("BestBd")
                obj_value = model.getAttr("ObjVal")
                mip_gap = model.getAttr("MIPGap")
                runtime = model.getAttr("Runtime")
                status_str = "Optimal" if status == cp.COPT.OPTIMAL else "Time Limit"

                return {
                    "solver": "COPT",
                    "status": status_str,
                    "lb": lb,
                    "objective": obj_value,
                    "gap": mip_gap,
                    "time": runtime
                }
            else:
                return {
                    "solver": "COPT",
                    "status": "Failed"
                }

        except cp.CoptError as e:
            return {
                "solver": "COPT",
                "status": f"Error: {str(e)}"
            }
