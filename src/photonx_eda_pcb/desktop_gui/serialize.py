import json
from .model import DesktopState,PanelState,DocumentTab
def dumps_desktop(s):return json.dumps({"panels":{k:v.__dict__ for k,v in sorted(s.panels.items())},"tabs":[t.__dict__ for t in s.tabs],"active_tab":s.active_tab,"status_message":s.status_message},sort_keys=True,separators=(",",":"))
def loads_desktop(text):
    d=json.loads(text);return DesktopState({k:PanelState(**v) for k,v in d.get("panels",{}).items()},[DocumentTab(**x) for x in d.get("tabs",[])],d.get("active_tab"),str(d.get("status_message","")))
