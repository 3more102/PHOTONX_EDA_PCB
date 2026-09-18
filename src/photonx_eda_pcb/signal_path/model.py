from dataclasses import dataclass
@dataclass(frozen=True)
class SignalPath:
    nodes:tuple[str,...]
    hops:int
    confidence:float=1.0
