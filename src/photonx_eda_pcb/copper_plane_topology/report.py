from .net_areas import net_areas
from .orphans import orphan_islands
def topology_report(t):
    return {"islands":len(t.islands),"nets":len(net_areas(t)),"orphan_islands":orphan_islands(t)}
