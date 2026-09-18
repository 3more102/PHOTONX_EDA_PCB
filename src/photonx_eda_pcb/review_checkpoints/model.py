from dataclasses import dataclass,field
@dataclass(frozen=True)
class CheckpointDecision:
    reviewer:str
    decision:str
    note:str=""
@dataclass
class ReviewCheckpoint:
    id:str
    title:str
    required_items:tuple[str,...]=()
    decisions:list[CheckpointDecision]=field(default_factory=list)
    closed:bool=False
