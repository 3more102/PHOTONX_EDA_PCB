class MigrationRegistry:
    def __init__(self):self._plans={}
    def add(self,p):
        if p.id in self._plans:raise ValueError("duplicate migration plan")
        self._plans[p.id]=p;return p
    def get(self,id):return self._plans[id]
    def all(self):return [self._plans[k] for k in sorted(self._plans)]
