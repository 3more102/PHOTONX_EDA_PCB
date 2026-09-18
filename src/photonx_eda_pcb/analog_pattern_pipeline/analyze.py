from photonx_eda_pcb.analog_blocks import detect_analog_blocks
from photonx_eda_pcb.analog_blocks.evidence import analog_evidence_records
from photonx_eda_pcb.analog_blocks.review import analog_review_items
from .model import AnalogAnalysis
def analyze_analog(identity_by_id,component_pin_nets,*,power_nets=(),ground_nets=(),pin_names_by_component=None):
    blocks=detect_analog_blocks(identity_by_id,component_pin_nets,power_nets=power_nets,ground_nets=ground_nets,pin_names_by_component=pin_names_by_component)
    return AnalogAnalysis(blocks,analog_evidence_records(blocks),analog_review_items(blocks))
