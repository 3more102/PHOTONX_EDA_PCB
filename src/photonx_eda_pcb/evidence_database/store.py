class EvidenceDatabase:
    def __init__(self):self._records={}
    def add(self,record):
        if record.id in self._records:raise ValueError("duplicate evidence id")
        self._records[record.id]=record;return record
    def upsert(self,record):self._records[record.id]=record;return record
    def get(self,id):return self._records[id]
    def all(self):return [self._records[k] for k in sorted(self._records)]
    def remove(self,id):return self._records.pop(id,None)
    def __len__(self):return len(self._records)
