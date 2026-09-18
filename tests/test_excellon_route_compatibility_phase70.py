from photonx_eda_pcb.capabilities import CAPABILITIES
def test_legacy_slots_routes_alias_remains_available():
    c={x.name:x for x in CAPABILITIES}["Excellon slots/routes"]
    assert c.status=="partial" and "G85" in c.note and "G00" in c.note
