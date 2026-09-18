from dataclasses import dataclass
@dataclass(frozen=True)
class SlotConnectivityCandidate:
    slot_id:str
    layers:tuple[str,...]
    pad_ids:tuple[str,...]
    net_ids:tuple[str,...]
    proven:bool
    conflict:bool
    confidence:float
    evidence:tuple[str,...]=()
