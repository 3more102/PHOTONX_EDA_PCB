from dataclasses import dataclass,field
@dataclass
class ManufacturingAudit:
    passed:bool
    blockers:list[str]=field(default_factory=list)
    warnings:list[str]=field(default_factory=list)
    metrics:dict[str,object]=field(default_factory=dict)
