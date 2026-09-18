from dataclasses import dataclass,field
@dataclass
class ReconstructionContext:
    inputs:dict=field(default_factory=dict)
    artifacts:dict=field(default_factory=dict)
    diagnostics:list[str]=field(default_factory=list)
    metrics:dict=field(default_factory=dict)
