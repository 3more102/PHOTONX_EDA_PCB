from dataclasses import dataclass
@dataclass(frozen=True)
class ResourceLimits:
    max_seconds:float=10.0
    max_items:int=1_000_000
