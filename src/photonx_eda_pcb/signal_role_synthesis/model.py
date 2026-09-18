from dataclasses import dataclass
@dataclass(frozen=True)
class SignalRole:
    net_id:str
    roles:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
