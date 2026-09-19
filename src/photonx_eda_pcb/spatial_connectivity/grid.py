from math import floor
class SpatialHashIndex:
    def __init__(self,cell_size=1.0):
        if cell_size<=0:raise ValueError("cell_size must be positive")
        self.cell_size=float(cell_size);self._boxes={};self._cells={};self._revision=0
    def _range(self,a,b):
        return range(floor(a/self.cell_size),floor(b/self.cell_size)+1)
    def insert(self,obj_id,box):
        oid=str(obj_id)
        if oid in self._boxes:raise ValueError("duplicate spatial id")
        self._boxes[oid]=box
        for ix in self._range(box.min_x,box.max_x):
            for iy in self._range(box.min_y,box.max_y):self._cells.setdefault((ix,iy),set()).add(oid)
        self._revision+=1
    @property
    def revision(self):return self._revision
    def query(self,box):
        ids=set()
        for ix in self._range(box.min_x,box.max_x):
            for iy in self._range(box.min_y,box.max_y):ids.update(self._cells.get((ix,iy),()))
        return sorted(x for x in ids if self._boxes[x].intersects(box))
    def box(self,obj_id):return self._boxes[str(obj_id)]
    def ids(self):return tuple(sorted(self._boxes))
    def boxes(self):return {k:self._boxes[k] for k in sorted(self._boxes)}
    def __len__(self):return len(self._boxes)
