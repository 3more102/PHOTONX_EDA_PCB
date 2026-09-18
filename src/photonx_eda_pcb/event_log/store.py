from .model import Event
class EventLog:
    def __init__(self):self._events=[]
    def append(self,kind,message,source="",object_id=None,data=None):
        e=Event(len(self._events)+1,str(kind),str(message),str(source),None if object_id is None else str(object_id),dict(data or {}));self._events.append(e);return e
    def all(self):return list(self._events)
    def since(self,seq):return [e for e in self._events if e.seq>int(seq)]
    def __len__(self):return len(self._events)
