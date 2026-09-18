from dataclasses import dataclass
@dataclass(frozen=True)
class RegulatorCandidate:
    component_id:str
    kind:str
    input_nets:tuple[str,...]
    output_nets:tuple[str,...]
    enable_nets:tuple[str,...]
    feedback_nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
