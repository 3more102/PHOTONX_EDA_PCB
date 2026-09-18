VALID_DOCK={"left","right","top","bottom","center"}
def validate_desktop_state(s):
    issues=[]
    if s.active_tab is not None and s.active_tab not in {t.id for t in s.tabs}:issues.append("DESKTOP_ACTIVE_TAB_MISSING")
    for p in s.panels.values():
        if p.dock not in VALID_DOCK:issues.append("DESKTOP_BAD_DOCK")
        if p.size<=0:issues.append("DESKTOP_PANEL_SIZE")
    return issues
