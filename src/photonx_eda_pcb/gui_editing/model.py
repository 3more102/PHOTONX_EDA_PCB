from dataclasses import dataclass,field
@dataclass(frozen=True)
class EditOperation:
    id:str
    kind:str
    object_id:str
    before:object
    after:object
    reason:str=""
@dataclass
class EditingState:
    pending:list[EditOperation]=field(default_factory=list)
    applied:list[EditOperation]=field(default_factory=list)
