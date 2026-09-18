class StageRegistry:
    def __init__(self):self._items={}
    def add(self,stage):
        if stage.name in self._items:raise ValueError(f"duplicate stage: {stage.name}")
        self._items[stage.name]=stage
    def ordered(self,names):
        return [self._items[n] for n in names if n in self._items]
