from dataclasses import dataclass, field
@dataclass(frozen=True)
class Diagnostic:
    severity:str
    code:str
    message:str
    line:int|None=None
@dataclass
class DiagnosticBag:
    items:list[Diagnostic]=field(default_factory=list)
    def add(self,severity,code,message,line=None): self.items.append(Diagnostic(severity,code,message,line))
    def errors(self): return [d for d in self.items if d.severity.lower()=="error"]
    @property
    def ok(self): return not self.errors()
