from photonx_eda_pcb.eco_tracking.model import EcoSet,EcoChange
from photonx_eda_pcb.eco_tracking.serialize import dumps_eco,loads_eco
def test_eco_roundtrip():
    e=EcoSet("E",[EcoChange("1","track","t","modify","x",True)],{})
    assert loads_eco(dumps_eco(e))==e
