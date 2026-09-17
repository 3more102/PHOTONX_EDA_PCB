from collections import defaultdict
class GridIndex:
    def __init__(self,cell_size=1.0):
        if cell_size<=0: raise ValueError("cell_size must be positive")
        self.cell_size=float(cell_size); self.cells=defaultdict(set); self.boxes={}
    def _keys(self,bbox):
        import math
        x0=math.floor(bbox.min_x/self.cell_size); x1=math.floor(bbox.max_x/self.cell_size)
        y0=math.floor(bbox.min_y/self.cell_size); y1=math.floor(bbox.max_y/self.cell_size)
        for x in range(x0,x1+1):
            for y in range(y0,y1+1): yield (x,y)
    def insert(self,key,bbox):
        self.boxes[key]=bbox
        for cell in self._keys(bbox): self.cells[cell].add(key)
    def query(self,bbox):
        candidates=set()
        for cell in self._keys(bbox): candidates.update(self.cells.get(cell,()))
        return sorted(key for key in candidates if self.boxes[key].intersects(bbox))
