class BaselineStore:
    def __init__(self):self._items={}
    def add(self,b):
        if b.id in self._items:raise ValueError("duplicate baseline")
        self._items[b.id]=b;return b
    def get(self,id):return self._items[id]
    def all(self):return [self._items[k] for k in sorted(self._items)]
