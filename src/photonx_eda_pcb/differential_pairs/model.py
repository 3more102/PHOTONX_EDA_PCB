from dataclasses import dataclass
@dataclass(frozen=True)
class PairCandidate:
    positive_net:str
    negative_net:str
    confidence:float
    reasons:tuple[str,...]=()
