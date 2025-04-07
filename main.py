import os
import json; 


from GRB_Optimizer import GRB_Optimizer
from COPT_Optimizer import COPT_Optimizer
from TSPProblem import TSPProblem
from plot import plot_tour

# 主函数
def main():
    # 选择三个TSP问题
    tsp_files = [
        os.path.join("data", "d657.tsp")
        # os.path.join("data", "u724.tsp"),
        # os.path.join("data", "d657.tsp"),
        # os.path.join("data", "rl1304.tsp")
    ]
    
    results = []
    
    for tsp_file in tsp_files:
        print(f"\nProcessing TSP Problem: {tsp_file}")
        
        # 读取TSP问题
        tsp_problem = TSPProblem(tsp_file)
        print(f"Problem Size: {tsp_problem.dimension} cities")
        grboptimizer = GRB_Optimizer(tsp_problem, timeLimit=20)
        coptoptimizer = COPT_Optimizer(tsp_problem, timeLimit=20)

        # # 使用Gurobi求解
        # print("\nSolving with Gurobi...")
        # gurobi_result = optimizer.solve_with_lazy_gurobi()
        # print(gurobi_result)
        # if gurobi_result["status"] != "Failed":
        #     plot_tour(tsp_problem.coordinates, gurobi_result["edges"])
        
        # 使用COPT求解
        print("\nSolving with COPT...")
        COPT_result = coptoptimizer.solve_with_lazy_copt()
        print(COPT_result)
        
        # 保存结果
        results.append({
            "problem": tsp_problem.name,
            "dimension": tsp_problem.dimension,
            "gurobi": gurobi_result,
            "copt": COPT_result
        })
        
    json.dump(results, open("out.json", "w"))
    

if __name__ == "__main__":
    main()