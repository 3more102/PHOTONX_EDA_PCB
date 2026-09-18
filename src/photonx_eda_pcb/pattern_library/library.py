class PatternLibrary:
    def __init__(self,patterns=()):self._items={p.name:p for p in patterns}
    def add(self,p):
        if p.name in self._items:raise ValueError("duplicate pattern")
        self._items[p.name]=p;return p
    def get(self,name):return self._items[name]
    def all(self):return [self._items[k] for k in sorted(self._items)]
