from photonx_eda_pcb.evidence_database import EvidenceRecord,EvidenceDatabase,query_evidence,validate_database
from photonx_eda_pcb.evidence_database.scoring import object_confidence
def test_evidence_database():
    db=EvidenceDatabase();db.add(EvidenceRecord("1","pad:1","geometry",.6,"gerber","","g1"));db.add(EvidenceRecord("2","pad:1","mask",.7,"mask","","g2"))
    assert len(query_evidence(db,object_id="pad:1"))==2
    assert object_confidence(db.all())>.7
    assert validate_database(db)==[]
