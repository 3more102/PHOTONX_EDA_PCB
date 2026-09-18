from dataclasses import dataclass,field
@dataclass(frozen=True)
class TraceLink:
    claim_id:str
    source_ids:tuple[str,...]=()
    artifact_ids:tuple[str,...]=()
    review_ids:tuple[str,...]=()
    object_ids:tuple[str,...]=()
    confidence:float=0.0
@dataclass
class TraceabilityMatrix:
    links:list[TraceLink]=field(default_factory=list)
