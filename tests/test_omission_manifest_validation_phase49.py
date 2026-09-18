from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest

def test_skipped_slot_requires_reason():
    data={"exported_slots":[],"skipped_slots":["S"],"issues":[]}
    assert "OMISSION_SKIPPED_SLOT_WITHOUT_REASON" in validate_omission_manifest(data)
