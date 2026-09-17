from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass(frozen=True)
class AuditRecord:
    action:str
    target:str
    detail:str=""
    actor:str="system"
    timestamp:str=""
    @classmethod
    def create(cls,action,target,detail="",actor="system"): return cls(action,target,detail,actor,datetime.now(timezone.utc).isoformat())
