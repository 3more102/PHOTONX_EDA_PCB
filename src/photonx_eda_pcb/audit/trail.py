class AuditTrail:
    def __init__(self): self._records=[]
    def append(self,record): self._records.append(record)
    def all(self): return tuple(self._records)
    def for_target(self,target): return tuple(record for record in self._records if record.target==target)
