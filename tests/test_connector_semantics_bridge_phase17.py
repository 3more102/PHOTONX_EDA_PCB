from photonx_eda_pcb.connector_pin_functions.model import ResolvedPinFunction
from photonx_eda_pcb.port_inference.model import PortCandidate
from photonx_eda_pcb.connector_semantics_bridge import pin_function_records,port_records,connector_review_items
from photonx_eda_pcb.connector_semantics_bridge.validation import validate_records
def test_connector_semantics_bridge():
    pins=[ResolvedPinFunction("J1","1","N1",None,0,("unresolved",),()),ResolvedPinFunction("J1","2","GND","ground",.99)]
    records=pin_function_records(pins)+port_records([PortCandidate("J1","power",("2",),("GND",),.9)])
    assert validate_records(records)==[]
    assert connector_review_items(pins)[0].kind=="connector_pin_unresolved"
