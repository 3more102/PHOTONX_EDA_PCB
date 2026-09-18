from photonx_eda_pcb.gui_editing.model import EditOperation
from photonx_eda_pcb.gui_editing.commands import edit_to_command
from photonx_eda_pcb.gui_editing.undo import edit_to_change
def test_edit_adapters():
    op=EditOperation("e","set_value","R1","1k","10k","bom")
    assert edit_to_command(op).name=="edit.set_value"
    assert edit_to_change(op).after=="10k"
