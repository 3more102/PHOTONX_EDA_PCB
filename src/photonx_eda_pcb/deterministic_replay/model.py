from dataclasses import dataclass
@dataclass(frozen=True)
class ReplayResult:
    passed:bool
    first_hash:str
    second_hash:str
    event_count:int
