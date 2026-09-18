class PresetStore:
    def __init__(self):self._items={}
    def add(self,p):
        if p.name in self._items:raise ValueError("duplicate preset")
        self._items[p.name]=p;return p
    def get(self,name):return self._items[name]
    def all(self):return [self._items[k] for k in sorted(self._items)]
