from photonx_eda_pcb.evidence_database import EvidenceRecord,EvidenceDatabase
from photonx_eda_pcb.evidence_database.serialize import dumps_database,loads_database
def test_evidence_db_roundtrip():
    db=EvidenceDatabase();db.add(EvidenceRecord("1","x","k",.5))
    assert loads_database(dumps_database(db)).all()==db.all()
