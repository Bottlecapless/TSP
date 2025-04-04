import os
import time
import numpy as np
import gurobipy as gp
# import coptpy as cp
from gurobipy import GRB


from TSPProblem import TSPProblem
from optimizer import Optimizer

# 主函数
def main():
    # 选择三个TSP问题
    tsp_files = [
        os.path.join("data", "u724.tsp"),
        os.path.join("data", "d657.tsp"),
        os.path.join("data", "rl1304.tsp")
    ]
    
    results = []
    
    for tsp_file in tsp_files:
        print(f"\n处理TSP问题: {tsp_file}")
        
        # 读取TSP问题
        tsp_problem = TSPProblem(tsp_file)
        print(f"问题规模: {tsp_problem.dimension} 个城市")
        
        optimizer = Optimizer(tsp_problem)
        # 使用Gurobi求解
        print("\n使用Gurobi求解...")
        gurobi_result = optimizer.solve_with_gurobi()
        print(f"Gurobi求解状态: {gurobi_result['status']}")
        print(f"Gurobi求解时间: {gurobi_result['time']:.2f} 秒")
        if 'objective' in gurobi_result:
            print(f"Gurobi目标值: {gurobi_result['objective']}")
            print(f"Gurobi Gap: {gurobi_result['gap']:.4f}")
        
        # # 使用COPT求解
        # print("\n使用COPT求解...")
        # copt_result = solve_with_copt(tsp_problem)
        # print(f"COPT求解状态: {copt_result['status']}")
        # print(f"COPT求解时间: {copt_result['time']:.2f} 秒")
        # if 'objective' in copt_result:
        #     print(f"COPT目标值: {copt_result['objective']}")
        #     print(f"COPT Gap: {copt_result['gap']:.4f}")
        
        # 保存结果
        results.append({
            "problem": tsp_problem.name,
            "dimension": tsp_problem.dimension,
            "gurobi": gurobi_result
            # "copt": copt_result
        })
    
    # 打印结果比较
    print("\n\n结果比较:")
    print("-" * 80)
    print(f"{'问题':<10} {'规模':<8} {'Gurobi状态':<15} {'Gurobi目标值':<15} {'Gurobi时间(秒)':<15} {'COPT状态':<15} {'COPT目标值':<15} {'COPT时间(秒)':<15}")
    print("-" * 80)
    
    for result in results:
        gurobi_obj = result['gurobi'].get('objective', '-')
        copt_obj = result['copt'].get('objective', '-')
        
        print(f"{result['problem']:<10} {result['dimension']:<8} {result['gurobi']['status']:<15} {gurobi_obj:<15} {result['gurobi']['time']:<15.2f} {result['copt']['status']:<15} {copt_obj:<15} {result['copt']['time']:<15.2f}")

if __name__ == "__main__":
    main()