class RecentProjects:
    def __init__(self,limit=10): self.limit=limit; self._items=[]
    def touch(self,path):
        value=str(path); self._items=[item for item in self._items if item!=value]; self._items.insert(0,value); self._items=self._items[:self.limit]
    def items(self): return tuple(self._items)
