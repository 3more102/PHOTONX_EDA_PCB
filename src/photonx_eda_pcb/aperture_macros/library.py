from dataclasses import dataclass
@dataclass(frozen=True)
class MacroRecord:
    name:str
    body:str
class MacroLibrary:
    def __init__(self): self._items={}
    def add(self,name,body): self._items[str(name)]=MacroRecord(str(name),str(body))
    def get(self,name): return self._items.get(str(name))
    def names(self): return tuple(sorted(self._items))
