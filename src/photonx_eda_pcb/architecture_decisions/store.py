class DecisionStore:
    def __init__(self):self._items={}
    def add(self,d):
        if d.id in self._items:raise ValueError("duplicate ADR")
        self._items[d.id]=d;return d
    def get(self,id):return self._items[id]
    def all(self):return [self._items[k] for k in sorted(self._items)]
