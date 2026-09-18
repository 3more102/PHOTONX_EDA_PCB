from photonx_eda_pcb.workspace_index import build_index
from photonx_eda_pcb.provenance_graph import build_provenance_graph
from photonx_eda_pcb.review_workflow import ReviewItem,ReviewQueue,enqueue
from photonx_eda_pcb.annotations import Annotation,AnnotationStore,add_annotation
from photonx_eda_pcb.design_rule_profiles import default_profile
from photonx_eda_pcb.evidence_database import EvidenceRecord,EvidenceDatabase
def test_phase6_flow():
    idx=build_index([{"path":"top.gbr","role":"gerber_copper"}]);assert len(idx.artifacts)==1
    g=build_provenance_graph([{"object_id":"t1","sources":["top.gbr"]}]);assert len(g.edges)==1
    q=ReviewQueue();enqueue(q,ReviewItem("r1","component_hypothesis","U1"))
    a=AnnotationStore();add_annotation(a,Annotation("a1","U1","verify package"))
    assert default_profile().min_track_mm>0
    db=EvidenceDatabase();db.add(EvidenceRecord("e1","U1","footprint",.6));assert len(db)==1
