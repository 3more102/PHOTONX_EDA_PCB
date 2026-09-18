from .model import DesktopState,PanelState
def default_layout():
    panels={"layers":PanelState("layers",True,"left",240),"inspector":PanelState("inspector",True,"right",320),"nets":PanelState("nets",True,"left",260),"violations":PanelState("violations",True,"bottom",220),"review":PanelState("review",False,"right",300)}
    return DesktopState(panels,[],None,"")
