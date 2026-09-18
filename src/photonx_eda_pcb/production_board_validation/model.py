from dataclasses import dataclass,field
@dataclass(frozen=True)
class ProductionValidationConfig:
    require_outline:bool=True
    require_connectivity:bool=True
    min_provenance_coverage:float=.95
    max_drc_errors:int=0
    max_erc_errors:int=0
@dataclass
class ProductionValidationResult:
    passed:bool
    blockers:list[str]=field(default_factory=list)
    warnings:list[str]=field(default_factory=list)
    metrics:dict[str,object]=field(default_factory=dict)
