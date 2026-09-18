from .model import PlaneTopology,PlaneIsland
def build_plane_topology(islands,contacts=()):
    vals=[]
    for i in islands:
        vals.append(i if isinstance(i,PlaneIsland) else PlaneIsland(str(i["id"]),str(i["layer"]),float(i["area_mm2"]),i.get("net_id"),tuple(i.get("touches",()))))
    adj={i.id:set(i.touches) for i in vals}
    for a,b in contacts:
        adj.setdefault(str(a),set()).add(str(b));adj.setdefault(str(b),set()).add(str(a))
    return PlaneTopology(vals,adj)
