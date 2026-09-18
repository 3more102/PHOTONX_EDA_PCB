def padstack_inference_report(result):
    if result.padstack is None:return {"slot_id":result.slot_id,"exportable":False,"blockers":list(result.blockers)}
    p=result.padstack
    return {"slot_id":result.slot_id,"exportable":True,"center":list(p.center),"angle_deg":p.angle_deg,"pad_size":list(p.pad_size),"pad_shape":p.pad_shape,"drill_size":list(p.drill_size),"layers":list(p.layers),"net_id":p.net_id,"pad_ids":list(p.pad_ids),"confidence":p.confidence,"evidence":list(p.evidence)}
