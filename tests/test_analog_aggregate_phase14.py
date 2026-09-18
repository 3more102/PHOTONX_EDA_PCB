from photonx_eda_pcb.analog_blocks import detect_analog_blocks,validate_analog_block
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_aggregate_detects_multiple_candidates():
    ids={"R1":I("resistor","10kΩ"),"R2":I("resistor","10kΩ"),"C1":I("capacitor","100nF")}
    pins={"R1":{"1":"VCC","2":"MID"},"R2":{"1":"MID","2":"GND"},"C1":{"1":"MID","2":"GND"}}
    out=detect_analog_blocks(ids,pins,power_nets=["VCC"],ground_nets=["GND"])
    kinds={x.kind for x in out}
    assert "voltage_divider" in kinds and "rc_filter" in kinds
    assert all(validate_analog_block(x)==[] for x in out)
