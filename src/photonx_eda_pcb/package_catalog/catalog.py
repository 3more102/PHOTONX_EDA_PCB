class PackageCatalog:
    def __init__(self,entries=()):self._items={e.name:e for e in entries}
    def add(self,e):
        if e.name in self._items:raise ValueError("duplicate package")
        self._items[e.name]=e;return e
    def get(self,name):return self._items[name]
    def all(self):return [self._items[k] for k in sorted(self._items)]
    def by_family(self,family):return [x for x in self.all() if x.family==family]
