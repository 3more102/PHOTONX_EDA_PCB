from photonx_eda_pcb.annotations import Annotation,AnnotationStore
from photonx_eda_pcb.annotations.serialize import dumps_annotations,loads_annotations
def test_annotation_roundtrip():
    s=AnnotationStore([Annotation("1","x","note")])
    assert loads_annotations(dumps_annotations(s)).items==s.items
