from photonx_eda_pcb.mechanical_features.measure import slot_geometry_descriptor
def pad_shape_name(shape):
    s=str(shape or "").upper()
    if s=="C":return "circle"
    if s=="O":return "oval"
    if s=="R":return "rect"
    return "rect"
def slot_geometry(slot):return slot_geometry_descriptor(slot)
def slot_export_status(slot):
    plating=str(getattr(slot,"plated","unknown")).lower().replace("_","-")
    if plating=="non-plated":return "export-npth"
    if plating=="plated":return "infer-plated-padstack"
    return "skip-unknown-plating"
