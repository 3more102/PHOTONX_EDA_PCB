def material_metrics(shape):
    if shape is None:return {"available":False,"area_mm2":0.0,"holes":0}
    holes=sum(len(p.interiors) for p in getattr(shape,"geoms",[shape]) if hasattr(p,"interiors"))
    return {"available":True,"area_mm2":round(float(shape.area),6),"holes":holes,"bounds":tuple(round(float(x),6) for x in shape.bounds)}
