from dataclasses import dataclass
@dataclass(frozen=True)
class Fault:
    id:str
    kind:str
    target:str
    value:object=None
@dataclass(frozen=True)
class FaultResult:
    fault_id:str
    detected:bool
    detector_output:object
