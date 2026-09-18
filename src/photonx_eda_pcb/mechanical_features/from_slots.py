from .model import SlotFeature
def slot_from_decoded(id,start,end,width_mm,plated="unknown"):
    return SlotFeature(str(id),(float(start[0]),float(start[1])),(float(end[0]),float(end[1])),float(width_mm),str(plated))
