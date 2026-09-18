from dataclasses import dataclass,field
@dataclass
class SelectionState:
    ids:list[str]=field(default_factory=list)
    primary:str|None=None
    def select(self,obj_id,add=False):
        x=str(obj_id)
        if not add:self.ids=[]
        if x not in self.ids:self.ids.append(x)
        self.primary=x;return self
    def clear(self):self.ids=[];self.primary=None;return self
