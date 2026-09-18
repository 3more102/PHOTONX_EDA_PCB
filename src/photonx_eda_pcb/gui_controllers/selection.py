class SelectionController:
    def __init__(self,state):self.state=state
    def replace(self,obj_id):return self.state.select(obj_id,False)
    def add(self,obj_id):return self.state.select(obj_id,True)
    def clear(self):return self.state.clear()
