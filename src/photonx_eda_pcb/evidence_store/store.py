from .record import EvidenceRecord
class EvidenceStore:
    def __init__(self): self._items={}
    def add(self,record:EvidenceRecord):
        if record.id in self._items and self._items[record.id]!=record: raise ValueError(f"evidence id collision: {record.id}")
        self._items[record.id]=record
    def get(self,evidence_id): return self._items.get(evidence_id)
    def all(self): return [self._items[key] for key in sorted(self._items)]
    def __len__(self): return len(self._items)
