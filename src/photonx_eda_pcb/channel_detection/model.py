from dataclasses import dataclass
@dataclass(frozen=True)
class ChannelCandidate:
    id:str
    instances:tuple[str,...]
    kind:str
    confidence:float
    evidence:tuple[str,...]=()
    differences:tuple[str,...]=()
