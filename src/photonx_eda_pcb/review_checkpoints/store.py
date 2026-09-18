class CheckpointStore:
    def __init__(self):self._items={}
    def add(self,c):
        if c.id in self._items:raise ValueError("duplicate checkpoint")
        self._items[c.id]=c;return c
    def get(self,id):return self._items[id]
    def all(self):return [self._items[k] for k in sorted(self._items)]
