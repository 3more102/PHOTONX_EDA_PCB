from photonx_eda_pcb.silkscreen_semantics.parser import parse_silkscreen_text
from photonx_eda_pcb.silkscreen_semantics.classification import classify_token
from photonx_eda_pcb.silkscreen_semantics.net_labels import net_label_candidates

def test_silk_classification():
    t=parse_silkscreen_text('R1 U2 GND foo')
    assert classify_token(t[0])=='reference_resistor'
    assert classify_token(t[1])=='reference_ic'
    assert net_label_candidates(t)==['GND']
