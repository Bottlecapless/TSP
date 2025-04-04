import numpy as np
import math
import os

# TSPProble
class TSPProblem:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = os.path.basename(file_path).split('.')[0]
        self.dimension = 0
        self.coordinates = {}
        self.distances = None
        self.read_tsp_file()
        self.calculate_distances()
    
    def read_tsp_file(self):
        """读取TSP文件"""
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            
            # 解析文件头部信息
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("DIMENSION"):
                    self.dimension = int(line.split(":")[1].strip())
                elif line.startswith("NODE_COORD_SECTION"):
                    i += 1
                    break
                i += 1
            
            # 读取坐标信息
            for j in range(i, i + self.dimension):
                if j < len(lines):
                    parts = lines[j].strip().split()
                    if len(parts) >= 3:
                        node_id = int(parts[0])
                        x = float(parts[1])
                        y = float(parts[2])
                        self.coordinates[node_id] = (x, y)
    
    def calculate_distances(self):
        """计算城市间的欧几里得距离"""
        n = self.dimension
        self.distances = np.zeros((n, n))
        
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i != j:
                    x1, y1 = self.coordinates[i]
                    x2, y2 = self.coordinates[j]
                    # 计算欧几里得距离并四舍五入到整数
                    self.distances[i-1, j-1] = round(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
                else:
                    self.distances[i-1, j-1] = 0