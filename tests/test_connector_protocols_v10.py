from photonx_eda_pcb.connector_pinout import infer_pinout
from photonx_eda_pcb.connector_pinout.protocols import compatible_protocols
from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
def test_connector_protocol_match():
    p=infer_pinout("J1",{"1":"a","2":"b"},{"a":"SCL","b":"SDA"})
    c=[ProtocolCandidate("i2c",("a","b"),.9,())]
    assert compatible_protocols(p,c)[0].protocol=="i2c"
