from dataclasses import dataclass,field
from typing import Callable
@dataclass(frozen=True)
class DagNode:
    name:str
    fn:Callable
    requires:tuple[str,...]=()
    produces:tuple[str,...]=()
    cacheable:bool=True
@dataclass
class DagRunResult:
    artifacts:dict[str,object]=field(default_factory=dict)
    executed:list[str]=field(default_factory=list)
    skipped:list[str]=field(default_factory=list)
    failed:list[tuple[str,str]]=field(default_factory=list)
