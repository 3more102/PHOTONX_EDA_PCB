from photonx_eda_pcb.annotations import Annotation,AnnotationStore,add_annotation,find_annotations,validate_annotations
def test_annotations():
    s=AnnotationStore();add_annotation(s,Annotation("1","pad:1","check solder mask","omar","review"))
    assert len(find_annotations(s,text="mask"))==1
    assert validate_annotations(s)==[]
