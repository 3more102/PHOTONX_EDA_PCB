from photonx_eda_pcb.protocol_detection import detect_protocols
from photonx_eda_pcb.connector_pinout import infer_pinout
from photonx_eda_pcb.rule_learning import learn_rules
from photonx_eda_pcb.desktop_gui import default_layout
def test_phase10_integration():
    protocols=detect_protocols({"a":"SCL","b":"SDA"})
    assert protocols[0].protocol=="i2c"
    pinout=infer_pinout("J1",{"1":"a","2":"b"},{"a":"SCL","b":"SDA"})
    assert len(pinout.pins)==2
    assert "min_track_mm" in learn_rules("x",track_widths=[.15,.2,.18]).rules
    assert "layers" in default_layout().panels
