from photonx_eda_pcb.gui_editing.model import EditOperation,EditingState
from photonx_eda_pcb.gui_editing.conflicts import conflicting_edits
from photonx_eda_pcb.gui_editing.review import review_items_for_edits
def test_sensitive_edit_review_and_conflict():
    s=EditingState([EditOperation("a","merge_nets","N1",None,"N2"),EditOperation("b","merge_nets","N1",None,"N3")],[])
    assert conflicting_edits(s)
    assert len(review_items_for_edits(s))==2
