class EditingController:
    def __init__(self,state):self.state=state
    def stage(self,op):
        if any(x.id==op.id for x in self.state.pending+self.state.applied):raise ValueError("duplicate edit id")
        self.state.pending.append(op);return op
    def apply(self,op_id):
        for i,x in enumerate(self.state.pending):
            if x.id==op_id:
                self.state.pending.pop(i);self.state.applied.append(x);return x
        raise KeyError(op_id)
    def discard(self,op_id):
        for i,x in enumerate(self.state.pending):
            if x.id==op_id:return self.state.pending.pop(i)
        raise KeyError(op_id)
