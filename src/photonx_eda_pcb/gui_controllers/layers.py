class LayerController:
    def __init__(self,state):self.state=state
    def show(self,layer):return self.state.set(layer,True)
    def hide(self,layer):return self.state.set(layer,False)
    def toggle(self,layer):return self.state.set(layer,not self.state.is_visible(layer))
