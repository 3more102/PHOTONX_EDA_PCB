from .union_find import UnionFind
from .model import ContactEdge,SolverResult

def solve_connectivity(object_ids,edges):
    uf=UnionFind(object_ids);accepted=[];diagnostics=[]
    for e in edges:
        edge=e if isinstance(e,ContactEdge) else ContactEdge(*e)
        if edge.a==edge.b:
            diagnostics.append({'severity':'warning','code':'SELF_CONTACT_EDGE','object':edge.a});continue
        if edge.confidence<0 or edge.confidence>1:
            diagnostics.append({'severity':'error','code':'CONTACT_CONFIDENCE_INVALID','edge':(edge.a,edge.b)});continue
        uf.union(edge.a,edge.b);accepted.append(edge)
    return SolverResult(uf.groups(),accepted,diagnostics)
