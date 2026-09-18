from photonx_eda_pcb.desktop_gui import default_layout,validate_desktop_state
from photonx_eda_pcb.desktop_gui.tabs import open_tab,close_tab,mark_tab_dirty
from photonx_eda_pcb.desktop_gui.panels import toggle_panel
def test_desktop_state():
    s=default_layout();open_tab(s,"a","Board","a.kicad_pcb");mark_tab_dirty(s,"a")
    assert s.active_tab=="a" and s.tabs[0].dirty
    before=s.panels["layers"].visible;toggle_panel(s,"layers");assert s.panels["layers"].visible!=before
    close_tab(s,"a");assert s.active_tab is None
    assert validate_desktop_state(s)==[]
