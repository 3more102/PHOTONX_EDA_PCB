from dataclasses import dataclass,field
@dataclass(frozen=True)
class GateFinding:
    severity:str;code:str;message:str;value:float|int|str|None=None;limit:float|int|str|None=None
@dataclass
class GateResult:
    passed:bool;findings:list[GateFinding]=field(default_factory=list);metrics:dict=field(default_factory=dict)
