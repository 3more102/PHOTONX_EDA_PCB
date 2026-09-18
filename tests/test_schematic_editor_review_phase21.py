from photonx_eda_pcb.schematic_editor.review import review_for_edit
def test_sensitive_schematic_edit_routes_to_review():
    x=review_for_edit("assign_reference","U1",.99)
    assert x is not None and x.priority==80
    assert review_for_edit("move","U1",.9) is None
