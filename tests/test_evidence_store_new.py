import pytest
from photonx_eda_pcb.evidence_store import EvidenceRecord,EvidenceStore
from photonx_eda_pcb.evidence_store.scoring import combined_confidence
def test_evidence_store_and_score():
    store=EvidenceStore(); store.add(EvidenceRecord("e1","geometry","a.gbr","touch",0.5,"P1")); store.add(EvidenceRecord("e2","drill","a.drl","hit",0.5,"P1"))
    assert len(store)==2 and combined_confidence(store.all())==0.75
def test_evidence_range_check():
    with pytest.raises(ValueError): EvidenceRecord("x","k","s","d",1.1)
