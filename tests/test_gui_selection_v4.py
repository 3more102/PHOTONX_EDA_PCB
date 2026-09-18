from photonx_eda_pcb.gui_interaction import SelectionState,LayerVisibility
def test_selection_and_layers():
    s=SelectionState().select("P1").select("P2",add=True)
    assert s.ids==["P1","P2"] and s.primary=="P2"
    l=LayerVisibility().set("F.Cu",False)
    assert not l.is_visible("F.Cu") and l.is_visible("B.Cu")
