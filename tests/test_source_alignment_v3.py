from photonx_eda_pcb.source_alignment import translation_fit,apply_transform,validate_alignment
from photonx_eda_pcb.source_alignment.error import rms_error
def test_translation_alignment():
    a=[(0,0),(1,1)];b=[(2,3),(3,4)]
    t=translation_fit(a,b)
    assert apply_transform((0,0),t)==(2.0,3.0)
    assert rms_error(a,b,t)==0
    assert validate_alignment(t)==[]
