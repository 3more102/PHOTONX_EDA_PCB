def slot_evidence(slot):
    return {"id":slot.id,"tool":slot.tool,"width_mm":slot.width_mm,"plated":slot.plated,"sources":[{"path":s.path,"line":s.line,"raw":s.raw} for s in slot.provenance.sources]}
