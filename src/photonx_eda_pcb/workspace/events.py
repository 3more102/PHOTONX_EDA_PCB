from dataclasses import dataclass
@dataclass(frozen=True)
class WorkspaceEvent:
    kind:str
    detail:str=""
class EventLog:
    def __init__(self): self._events=[]
    def append(self,event): self._events.append(event)
    def events(self): return tuple(self._events)
