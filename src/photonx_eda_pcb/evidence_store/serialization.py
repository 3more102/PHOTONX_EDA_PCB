from dataclasses import asdict
from .record import EvidenceRecord
def evidence_to_dict(record): return asdict(record)
def evidence_from_dict(value): return EvidenceRecord(**value)
