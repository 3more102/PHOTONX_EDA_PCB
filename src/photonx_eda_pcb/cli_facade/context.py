from dataclasses import dataclass,field
@dataclass
class CliContext:
    services:object|None=None
    capabilities:list[str]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)
