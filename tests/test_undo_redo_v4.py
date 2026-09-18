from photonx_eda_pcb.undo_redo import Change,UndoRedoStack
def test_undo_redo():
    state={};s=UndoRedoStack();c=Change("x",None,7)
    s.do(state,c);assert state["x"]==7
    s.undo(state);assert "x" not in state
    s.redo(state);assert state["x"]==7
