from types import SimpleNamespace
from photonx_eda_pcb.ipc356.model import Ipc356Record
from photonx_eda_pcb.ipc356.map_records import map_records_to_pads
from photonx_eda_pcb.ipc356.net_labels import net_labels
def test_ipc356_to_labels():
    pads=[SimpleNamespace(id="P1",center=SimpleNamespace(x=0.0,y=0.0))]
    rec=[Ipc356Record("317","GND","J1","2",0.01,0.0,"TOP","")]
    ev,miss=map_records_to_pads(rec,pads,.05)
    assert not miss
    assert net_labels(ev)=={"P1":"GND"}
