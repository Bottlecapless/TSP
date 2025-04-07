import coptpy as cp
from coptpy import COPT
from itertools import combinations
from collections import defaultdict

class TSPCallback(cp.CallbackBase):
    def __init__(self, model, x, nodes):
        super().__init__(model)
        self.x = x
        self.nodes = nodes

    def callback(self):
        if self.where == COPT.CBCONTEXT_MIPSOL:
            sol = self.getIncumbent(self.x)
            edges = [(i, j) for (i, j), val in sol.items() if val > 0.5]
            try:
                subtour = self._shortest_subtour(edges)
                if len(subtour) < len(self.nodes):
                    self.addLazyConstr(
                        cp.quicksum(self.x[i, j] for i, j in combinations(subtour, 2)) <= len(subtour) - 1
                    )
            except ValueError as ve:
                print("Skipping invalid solution in callback:", ve)
            except Exception as e:
                print("Callback failed with unexpected error:", e)
                self.abort()

    def _shortest_subtour(self, edges):
        neighbors = defaultdict(list)
        for i, j in edges:
            neighbors[i].append(j)
            neighbors[j].append(i)

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
        x = model.addVars(edges, vtype=COPT.BINARY, name="x")
        model.setObjective(cp.quicksum(dist_dict[i, j] * x[i, j] for (i, j) in edges), sense=COPT.MINIMIZE)

        for i in nodes:
            model.addConstr(cp.quicksum(x[min(i, j), max(i, j)] for j in nodes if i != j) == 2)

        init_tour = self._generate_nearest_neighbor_tour()
        for i, j in init_tour:
            x[i, j].Start = 1

        model.setParam(COPT.Param.TimeLimit, self.timeLimit)
        model.setParam(COPT.Param.HeurLevel, 3)
        model.setParam(COPT.Param.Threads, 8)
        model.setParam(COPT.Param.Presolve, 2)
        model.setParam(COPT.Param.MIPStart, 1)

        cb = TSPCallback(model, x, nodes)
        model.solve(cb)

        if model.status == COPT.OPTIMAL or model.status == COPT.TIME_LIMIT:
            vals = {k: x[k].X for k in x}
            edges_used = [(i, j) for (i, j), val in vals.items() if val > 0.5]
            return {
                "solver": "COPT",
                "status": "Optimal" if model.status == COPT.OPTIMAL else "Time Limit",
                "edges": edges_used,
                "objective": model.objval,
                "gap": model.mipgap,
                "time": model.runtime
            }
        else:
            return {"solver": "COPT", "status": "Failed"}