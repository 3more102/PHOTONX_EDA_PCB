from photonx_eda_pcb.capabilities import CAPABILITIES
def test_excellon_slot_capability_is_partial_not_full_route_support():
    c={x.name:x for x in CAPABILITIES}["Excellon slots/routes"]
    assert c.status=="partial"
    assert "G85" in c.note and "G00" in c.note
