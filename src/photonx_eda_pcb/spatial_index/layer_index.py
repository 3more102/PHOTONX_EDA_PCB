from .grid import GridIndex
class LayerSpatialIndex:
    def __init__(self,cell_size=1.0): self.cell_size=cell_size; self.layers={}
    def for_layer(self,layer): return self.layers.setdefault(layer,GridIndex(self.cell_size))
