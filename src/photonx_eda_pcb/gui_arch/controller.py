from .selection import select_object,clear_selection
from .viewport import zoom_by
from .net_highlight import highlight_net,clear_highlight
class AppController:
    def __init__(self,state): self.state=state
    def dispatch(self,name,payload=None):
        p=payload or {}
        if name=='select': return select_object(self.state,p.get('id'))
        if name=='clear_selection': return clear_selection(self.state)
        if name=='highlight_net': return highlight_net(self.state,p.get('net_id'))
        if name=='clear_highlight': return clear_highlight(self.state)
        if name=='zoom': return zoom_by(self.state,float(p.get('factor',1.0)))
        raise KeyError(name)
