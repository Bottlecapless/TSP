import os
import time
import math
import numpy as np
import gurobipy as gp
# import coptpy as cp
from gurobipy import GRB

from optimizer import Optimizer
from TSPProblem import TSPProblem

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
        optimizer = Optimizer(tsp_problem)

        # 使用Gurobi求解
        print("\nSolving with Gurobi...")
        gurobi_result = optimizer.solve_with_gurobi()
        print(gurobi_result)
        
        # # 使用COPT求解
        # print("\nSolving with COPT...")
        # copt_result = solve_with_copt(tsp_problem)
        # print(f"COPT Solution Status: {copt_result['status']}")
        # print(f"COPT Solution Time: {copt_result['time']:.2f} seconds")
        # if 'objective' in copt_result:
        #     print(f"COPT Objective Value: {copt_result['objective']}")
        #     print(f"COPT Gap: {copt_result['gap']:.4f}")
        
        # 保存结果
        results.append({
            "problem": tsp_problem.name,
            "dimension": tsp_problem.dimension,
            "gurobi": gurobi_result
            # "copt": copt_result
        })
    
    # 打印结果比较
    print("\n\nResults Comparison:")
    print("-" * 80)
    print(f"{'Problem':<10} {'Size':<8} {'Gurobi Status':<15} {'Gurobi Obj':<15} {'Gurobi Time(s)':<15} {'COPT Status':<15} {'COPT Obj':<15} {'COPT Time(s)':<15}")
    print("-" * 80)
    
    for result in results:
        gurobi_obj = result['gurobi'].get('objective', '-')
        # copt_obj = result['copt'].get('objective', '-')
        
        print(f"{result['problem']:<10} {result['dimension']:<8} {result['gurobi']['status']:<15} {gurobi_obj:<15} {result['gurobi']['time']:<15.2f} {result['copt']['status']:<15} {copt_obj:<15} {result['copt']['time']:<15.2f}")

if __name__ == "__main__":
    main()