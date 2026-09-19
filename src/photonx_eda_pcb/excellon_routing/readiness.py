from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class RouteExportReadiness:
    exportable:tuple[str,...]
    omitted:tuple[str,...]
    reasons:dict[str,str]
    @property
    def fully_resolved(self):return not self.omitted


def is_exact_npth_slot_route(route):
    plating=str(getattr(route,"plated","unknown")).lower().replace("_","-")
    if plating!="non-plated":return False
    points=tuple(getattr(route,"points",()))
    if len(points)!=2:return False
    try:
        x0,y0=map(float,points[0]);x1,y1=map(float,points[1]);width=float(route.width_mm)
    except (TypeError,ValueError,OverflowError):
        return False
    values=(x0,y0,x1,y1,width)
    return all(isfinite(value) for value in values) and width>0 and (x0,y0)!=(x1,y1)


def assess_route_export_readiness(routes):
    exportable=[]
    omitted=[]
    reasons={}
    for route in sorted(routes,key=lambda item:item.id):
        if is_exact_npth_slot_route(route):
            exportable.append(route.id)
        else:
            omitted.append(route.id)
            reasons[route.id]="KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
    return RouteExportReadiness(tuple(exportable),tuple(omitted),reasons)
