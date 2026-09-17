class ArtifactCatalog:
    def __init__(self):self._items={}
    def add(self,artifact):
        if artifact.name in self._items:raise ValueError(f'duplicate artifact {artifact.name}')
        self._items[artifact.name]=artifact;return artifact
    def get(self,name):return self._items[name]
    def find_kind(self,kind):return [a for a in self._items.values() if a.kind==kind]
    def names(self):return sorted(self._items)
    def __len__(self):return len(self._items)
