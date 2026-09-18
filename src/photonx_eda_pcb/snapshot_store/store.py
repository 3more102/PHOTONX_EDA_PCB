from .model import Snapshot
from .hash import payload_hash
class SnapshotStore:
    def __init__(self):self._items={};self._head=None
    def create(self,payload,label="",parent_id=None,snapshot_id=None):
        parent=self._head if parent_id is None else parent_id
        sid=snapshot_id or payload_hash(f"{parent}|{payload}|{label}")[:24]
        if sid in self._items:raise ValueError("duplicate snapshot id")
        if parent is not None and parent not in self._items:raise KeyError(parent)
        s=Snapshot(sid,parent,str(payload),payload_hash(payload),str(label));self._items[sid]=s;self._head=sid;return s
    def get(self,id):return self._items[id]
    def head(self):return self._items.get(self._head)
    def ids(self):return sorted(self._items)
    def lineage(self,id=None):
        cur=self._head if id is None else id;out=[]
        while cur is not None:
            s=self._items[cur];out.append(s);cur=s.parent_id
        return out
