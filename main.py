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
        os.path.join("data", "d657.tsp"),
        os.path.join("data", "rat575.tsp"),
        os.path.join("data", "u1060.tsp")
    ]
    tsp_names = [
        "outd657.json",
        "outrat575.json",
        "outu1060.json"
    ]

    results = []
    
    for fileIndex in range(len(tsp_files)):
        tsp_file = tsp_files[fileIndex]
        tsp_name = tsp_names[fileIndex]

        print(f"\nProcessing TSP Problem: {tsp_file}")
        # 读取TSP问题
        tsp_problem = TSPProblem(tsp_file)
        print(f"Problem Size: {tsp_problem.dimension} cities")
        grboptimizer = GRB_Optimizer(tsp_problem, timeLimit=timeLimit)
        # return
        coptoptimizer = COPT_Optimizer(tsp_problem, timeLimit=timeLimit)

        # 使用Gurobi求解
        print("\nSolving with Gurobi...")
        gurobi_result = grboptimizer.solve_with_lazy_gurobi()
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
        json.dump(results, open(tsp_name, "w"))
        print(f"Problem {tsp_file} Finished.")
    

if __name__ == "__main__":
    main(timeLimit=20)