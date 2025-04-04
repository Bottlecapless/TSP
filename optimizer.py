import gurobipy as gp
from gurobipy import GRB

from TSPProblem import TSPProblem

class Optimizer:
    def __init__(self, tsp_problem):
        self.tsp_problem = tsp_problem
        self.n = tsp_problem.dimension
        self.distances = tsp_problem.distances
        self.x = {}
        self.u = {}
        self.model = None

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
            
            # 设置求解时间限制（30分钟）
            model.setParam('TimeLimit', 600)
            
            # 求解模型
            model.optimize()
            
            if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
                lb = model.ObjBound
                obj_value = model.ObjVal
                gap = model.MIPGap
                status = "Optimal" if model.status == GRB.OPTIMAL else "Time Limit"
                runTime = model.Runtime

                # 构建路径
                tour = [0]  # 从节点0开始
                current = 0
                while len(tour) < n:
                    for j in range(n):
                        if j != current and (current, j) in x and x[current, j].x > 0.5:
                            tour.append(j)
                            current = j
                            break
                
                return {
                    "solver": "Gurobi",
                    "status": status,
                    "lb": lb,
                    "objective": obj_value,
                    "gap": gap,
                    "time": runTime,
                    "tour": tour
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
        


        # 使用COPT求解TSP问题
# def solve_with_copt(tsp_problem):
#     start_time = time.time()
    
#     try:
#         # 创建COPT环境和模型
#         env = cp.Envr()
#         model = env.createModel("TSP_COPT")
        
#         n = tsp_problem.dimension
#         distances = tsp_problem.distances
        
#         # 创建变量
#         x = {}
#         for i in range(n):
#             for j in range(n):
#                 if i != j:
#                     x[i, j] = model.addVar(vtype=cp.BINARY, name=f'x_{i}_{j}')
        
#         # 添加约束：每个城市只能进入一次
#         for j in range(n):
#             model.addConstr(cp.quicksum(x[i, j] for i in range(n) if i != j) == 1)
        
#         # 添加约束：每个城市只能离开一次
#         for i in range(n):
#             model.addConstr(cp.quicksum(x[i, j] for j in range(n) if i != j) == 1)
        
#         # 消除子回路约束（使用MTZ公式）
#         u = {}
#         for i in range(1, n):
#             u[i] = model.addVar(lb=0, ub=n-1, vtype=cp.INTEGER, name=f'u_{i}')
        
#         for i in range(1, n):
#             for j in range(1, n):
#                 if i != j:
#                     model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)
        
#         # 设置目标函数
#         model.setObjective(cp.quicksum(distances[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j), cp.MINIMIZE)
        
#         # 设置求解时间限制（30分钟）
#         model.setParam(cp.TIMELIMIT, 1800)
        
#         # 求解模型
#         model.solve()
        
#         # 获取结果
#         solve_time = time.time() - start_time
        
#         if model.status == cp.OPTIMAL or model.status == cp.TIMEOUT:
#             obj_value = model.objval
#             gap = model.getMIPGap()
#             status = "Optimal" if model.status == cp.OPTIMAL else "Time Limit"
            
#             # 构建路径
#             tour = [0]  # 从节点0开始
#             current = 0
#             while len(tour) < n:
#                 for j in range(n):
#                     if j != current and (current, j) in x and model.getValue(x[current, j]) > 0.5:
#                         tour.append(j)
#                         current = j
#                         break
            
#             return {
#                 "solver": "COPT",
#                 "status": status,
#                 "objective": obj_value,
#                 "gap": gap,
#                 "time": solve_time,
#                 "tour": tour
#             }
#         else:
#             return {
#                 "solver": "COPT",
#                 "status": "Failed",
#                 "time": solve_time
#             }
    
#     except Exception as e:
#         solve_time = time.time() - start_time
#         return {
#             "solver": "COPT",
#             "status": f"Error: {str(e)}",
#             "time": solve_time
#         }