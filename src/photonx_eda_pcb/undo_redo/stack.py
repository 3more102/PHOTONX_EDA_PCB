from .patch import apply_change,revert_change
class UndoRedoStack:
    def __init__(self):self.undo_stack=[];self.redo_stack=[]
    def do(self,state,change):
        apply_change(state,change);self.undo_stack.append(change);self.redo_stack.clear();return state
    def undo(self,state):
        if not self.undo_stack:return state
        c=self.undo_stack.pop();revert_change(state,c);self.redo_stack.append(c);return state
    def redo(self,state):
        if not self.redo_stack:return state
        c=self.redo_stack.pop();apply_change(state,c);self.undo_stack.append(c);return state
