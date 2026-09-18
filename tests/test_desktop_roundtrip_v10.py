from photonx_eda_pcb.desktop_gui import default_layout
from photonx_eda_pcb.desktop_gui.serialize import dumps_desktop,loads_desktop
def test_desktop_roundtrip():
    s=default_layout();q=loads_desktop(dumps_desktop(s))
    assert set(q.panels)==set(s.panels)
