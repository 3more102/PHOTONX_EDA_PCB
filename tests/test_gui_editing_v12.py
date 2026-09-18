from photonx_eda_pcb.gui_editing import EditOperation,EditingState,EditingController,validate_edit
def test_stage_apply_edit():
    s=EditingState();c=EditingController(s);op=EditOperation("e1","rename_net","N1","N1","GND","reviewed")
    c.stage(op);assert s.pending==[op] and validate_edit(op)==[]
    assert c.apply("e1")==op and not s.pending and s.applied==[op]
