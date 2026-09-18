def panel_report(panel):
    return {"board_instances":len(panel.boards),"rail_width_mm":panel.rail_width_mm,"confidence":panel.confidence,"evidence":list(panel.evidence)}
