from dataclasses import dataclass,field
@dataclass(frozen=True)
class ContactEdge:
    a:str;b:str;kind:str='geometric_contact';confidence:float=1.0;reason:str=''
@dataclass
class SolverResult:
    groups:list[list[str]]=field(default_factory=list);edges:list[ContactEdge]=field(default_factory=list);diagnostics:list[dict]=field(default_factory=list)
    def object_count(self):return sum(len(g) for g in self.groups)
