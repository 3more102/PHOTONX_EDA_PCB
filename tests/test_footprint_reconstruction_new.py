from types import SimpleNamespace
from photonx_eda_pcb.footprint_reconstruction.engine import reconstruct_footprint
from photonx_eda_pcb.footprint_reconstruction.validation import validate_reconstruction

def p(i,x):return SimpleNamespace(id=i,center=SimpleNamespace(x=x,y=0.0),drill=.8)

def test_footprint_reconstruction_two_pin():
    fp=reconstruct_footprint('F1',[p('1',0),p('2',2.54)],reference='R1')
    assert fp.package_hint=='TWO_PIN_THT'
    assert fp.reference=='R1'
    assert validate_reconstruction(fp)==[]
