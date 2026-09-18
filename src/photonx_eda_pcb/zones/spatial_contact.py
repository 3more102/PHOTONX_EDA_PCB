from photonx_eda_pcb.spatial_connectivity import AABB,SpatialHashIndex
from photonx_eda_pcb.connectivity.geometry import copper_shape
from .geometry import island_shape

def _box(shape):
    x0,y0,x1,y1=shape.bounds
    return AABB(float(x0),float(y0),float(x1),float(y1))

def zone_copper_contacts(zone,objects,*,cell_size_mm=2.0):
    items=[o for o in objects if getattr(o,"layer",None)==zone.layer]
    if not items:return {}
    shapes={o.id:copper_shape(o) for o in items};idx=SpatialHashIndex(float(cell_size_mm))
    for o in items:idx.insert(o.id,_box(shapes[o.id]))
    out={}
    for island in zone.islands:
        z=island_shape(island)
        if z.is_empty:
            out[island.id]=();continue
        ids=[oid for oid in idx.query(_box(z)) if z.intersects(shapes[oid])]
        out[island.id]=tuple(sorted(ids))
    return out

def zone_contact_candidates(zone,objects,*,cell_size_mm=2.0):
    items=[o for o in objects if getattr(o,"layer",None)==zone.layer]
    brute=len(items)*len(zone.islands)
    contacts=zone_copper_contacts(zone,items,cell_size_mm=cell_size_mm)
    exact=sum(len(v) for v in contacts.values())
    return {"bruteforce_pairs":brute,"exact_contacts":exact}
