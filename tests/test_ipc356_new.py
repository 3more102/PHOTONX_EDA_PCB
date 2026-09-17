from photonx_eda_pcb.ipc356 import parse_ipc356
from photonx_eda_pcb.ipc356.index import records_by_net
def test_ipc356_subset():
    text='C comment\n317 NET=GND REF=J1 PIN=2 X=001000 Y=002000 SIDE=TOP\n317 NET=VCC REF=J1 PIN=1 X=003000 Y=002000 SIDE=TOP\n'
    records=parse_ipc356(text)
    assert len(records)==2 and records[0].x==1.0 and records[0].y==2.0
    assert set(records_by_net(records))=={'GND','VCC'}
