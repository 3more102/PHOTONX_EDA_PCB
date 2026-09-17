from dataclasses import dataclass,field
from typing import Callable
@dataclass(frozen=True)
class StageResult:
    name:str;ok:bool;outputs:tuple[str,...]=();diagnostics:tuple[dict,...]=();metadata:dict=field(default_factory=dict)
@dataclass
class Stage:
    name:str;fn:Callable;requires:tuple[str,...]=();provides:tuple[str,...]=()
    def run(self,ctx):return self.fn(ctx)
