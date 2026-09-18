from dataclasses import dataclass
@dataclass(frozen=True)
class UnifiedIssue:
    source:str
    code:str
    severity:str
    message:str
    object_id:str|None=None
