from dataclasses import dataclass
@dataclass(frozen=True)
class ChangeControlDecision:
    passed:bool
    blockers:tuple[str,...]
    change_count:int
    snapshot_head:str|None
    event_count:int
