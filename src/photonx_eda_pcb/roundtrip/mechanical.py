from math import hypot
def canonical_slot(slot):
    x0,y0=map(float,slot.start);x1,y1=map(float,slot.end)
    cx=(x0+x1)/2;cy=(y0+y1)/2;centerline=hypot(x1-x0,y1-y0);overall=centerline+float(slot.width_mm)
    return (round(cx,6),round(cy,6),round(overall,6),round(float(slot.width_mm),6),str(slot.plated).replace("_","-"))

def compare_mechanical_slots(expected_slots,observed_slots):
    a=sorted(canonical_slot(x) for x in expected_slots);b=sorted(canonical_slot(x) for x in observed_slots)
    return {"equal":a==b,"expected":a,"observed":b,"missing":sorted(set(a)-set(b)),"unexpected":sorted(set(b)-set(a))}
