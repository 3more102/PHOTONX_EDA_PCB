from photonx_eda_pcb.drc.model import DrcIssue
from photonx_eda_pcb.geometry_kernel import object_shape
from .geometry import route_shape
def check_route_copper_clearance(routes,board,minimum_mm=.15):
    out=[];copper=[*board.tracks,*board.pads,*getattr(board,"regions",())]
    for route in routes:
        rs=route_shape(route)
        for obj in copper:
            d=rs.distance(object_shape(obj))
            if d<float(minimum_mm):
                sev="error" if str(route.plated).lower().replace("_","-")=="non-plated" else "warning"
                out.append(DrcIssue(sev,"ROUTE_COPPER_CLEARANCE",f"routed-feature clearance {d:.6f} mm below {minimum_mm} mm",(route.id,obj.id)))
    return sorted(out,key=lambda x:x.object_ids)
