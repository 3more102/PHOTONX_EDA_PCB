from photonx_eda_pcb.parsers.gerber_parts.region_state import RegionState
from photonx_eda_pcb.parsers.gerber_parts.polarity import parse_polarity
from photonx_eda_pcb.parsers.gerber_parts.step_repeat import parse_step_repeat
def test_region():
 r=RegionState(); r.begin(); r.add(1,2); assert r.end()==((1,2),) and not r.active
def test_polarity(): assert parse_polarity('%LPC*%')=='clear'
def test_sr(): assert parse_step_repeat('%SRX2Y3I10.0J5.0*%')['y']==3
