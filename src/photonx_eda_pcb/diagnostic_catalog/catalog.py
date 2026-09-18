class DiagnosticCatalog:
    def __init__(self):self._items={}
    def add(self,item):
        if item.code in self._items:raise ValueError(f"duplicate diagnostic: {item.code}")
        self._items[item.code]=item;return item
    def get(self,code):return self._items[str(code)]
    def find(self,text):
        q=str(text).lower();return [x for x in self.all() if q in x.code.lower() or q in x.title.lower() or q in x.description.lower()]
    def all(self):return [self._items[k] for k in sorted(self._items)]
