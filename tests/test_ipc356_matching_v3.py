from types import SimpleNamespace
from photonx_eda_pcb.ipc356.model import Ipc356Record
from photonx_eda_pcb.ipc356.map_records import map_records_to_pads
from photonx_eda_pcb.ipc356.coverage import coverage
def test_ipc356_maps_to_pad():
    p=SimpleNamespace(id="P1",center=SimpleNamespace(x=1.0,y=2.0))
    r=Ipc356Record("317","GND","U1","1",1.02,2.0,"TOP","")
    ev,miss=map_records_to_pads([r],[p],.05)
    assert len(ev)==1 and not miss and ev[0].net_name=="GND"
    assert coverage([r],ev)==1.0
