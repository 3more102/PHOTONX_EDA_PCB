from photonx_eda_pcb.wire_routing.segments import route_length
def layout_quality(result):
    total=sum(route_length(r) for r in result.routes)
    penalty=result.crossings*25.0
    score=1.0/(1.0+total/1000.0+penalty/100.0)
    return {"wire_length":round(total,6),"crossings":result.crossings,"score":round(score,6)}
