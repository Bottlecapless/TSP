import os
import json; 


from GRB_Optimizer import GRB_Optimizer
from COPT_Optimizer import COPT_Optimizer
from TSPProblem import TSPProblem
from plot import plot_tour

# 主函数
def main(timeLimit):
    # 选择三个TSP问题
    tsp_files = [
        os.path.join("data", "d657.tsp")
        # os.path.join("data", "u724.tsp")
        # os.path.join("data", "u1060.tsp")
    ]
    
    results = []
    
    for tsp_file in tsp_files:
        print(f"\nProcessing TSP Problem: {tsp_file}")
        
        # 读取TSP问题
        tsp_problem = TSPProblem(tsp_file)
        print(f"Problem Size: {tsp_problem.dimension} cities")
        # grboptimizer = GRB_Optimizer(tsp_problem, timeLimit=timeLimit)
        coptoptimizer = COPT_Optimizer(tsp_problem, timeLimit=timeLimit)

        # 使用Gurobi求解
        print("\nSolving with Gurobi...")
        # gurobi_result = grboptimizer.solve_with_lazy_gurobi()
        
        # 使用COPT求解
        print("\nSolving with COPT...")
        COPT_result = coptoptimizer.solve_with_lazy_copt()
        
        # 保存结果
        results.append({
            "problem": tsp_problem.name,
            "dimension": tsp_problem.dimension,
            "gurobi": gurobi_result,
            "copt": COPT_result
        })
        
    json.dump(results, open("out.json", "w"))
    

if __name__ == "__main__":
    main(timeLimit=600)