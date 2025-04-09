import coptpy as cp
from coptpy import COPT

class COPT_Optimizer:
    def __init__(self, tsp_problem, timeLimit=120):
        self.tsp_problem = tsp_problem
        self.n = tsp_problem.dimension
        self.distances = tsp_problem.distances
        self.model = None
        self.timeLimit = timeLimit

    def _generate_nearest_neighbor_tour(self):
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

        tour.append((min(current, 0), max(current, 0)))
        return tour

    def solve_with_lazy_copt(self):
        env = cp.Envr()
        model = env.createModel("TSP_Lazy")

        n = self.n
        nodes = list(range(n))
        dist = self.distances
        dist_dict = self.tsp_problem.get_distance_dict()
        edges = list(dist_dict.keys())
        x = model.addVars(edges, vtype=COPT.BINARY)
        model.setObjective(cp.quicksum(dist_dict[i, j] * x[i, j] for (i, j) in edges), sense=COPT.MINIMIZE)

        for i in nodes:
            model.addConstr(cp.quicksum(x[min(i, j), max(i, j)] for j in nodes if i != j) == 2)

        init_tour = self._generate_nearest_neighbor_tour()
        for i, j in init_tour:
            model.setMipStart(x[i,j],1)

        model.setParam(COPT.Param.TimeLimit, self.timeLimit)
        model.setParam(COPT.Param.HeurLevel, 3)
        model.setParam(COPT.Param.Threads, 8)
        model.setParam(COPT.Param.Presolve, 2)
        model.setParam(COPT.Param.RelGap, 0.0000001)

        model.solve()

        if model.status == COPT.OPTIMAL or model.status == COPT.TIMEOUT:
            vals = {k: x[k].X for k in x}
            edges_used = [(i, j) for (i, j), val in vals.items() if val > 0.5]
            return {
                "solver": "COPT",
                "status": "Optimal" if model.status == COPT.OPTIMAL else "Time Limit",
                "lb": model.getAttr("BestBnd"),
                "objective": model.objval,
                "gap": model.getAttr("BestGap"),
                "time": model.getAttr("SolvingTime"),
                "edges": edges_used
            }
        else:
            return {"solver": "COPT", "status": "Failed"}