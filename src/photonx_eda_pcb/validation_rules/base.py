from dataclasses import dataclass
@dataclass(frozen=True)
class RuleIssue:
    severity:str
    code:str
    message:str
    object_id:str|None=None
