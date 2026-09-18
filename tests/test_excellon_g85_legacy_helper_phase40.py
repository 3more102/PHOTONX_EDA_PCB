from photonx_eda_pcb.parsers.excellon_parts.slots import parse_slot_command,is_canned_slot
def test_slot_helper_accepts_canonical_and_legacy_forms():
    assert parse_slot_command("X1Y2G85X3Y4")==("1","2","3","4")
    assert parse_slot_command("G85X1Y2X3Y4")==("1","2","3","4")
    assert is_canned_slot("X1Y2G85X3Y4")
