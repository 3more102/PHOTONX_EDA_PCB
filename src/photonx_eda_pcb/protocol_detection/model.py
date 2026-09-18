from dataclasses import dataclass
@dataclass(frozen=True)
class ProtocolCandidate:
    protocol:str
    net_ids:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
