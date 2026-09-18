from .model import ProvenanceNode,ProvenanceEdge,ProvenanceGraph
def build_provenance_graph(records):
    g=ProvenanceGraph()
    for r in records:
        oid=str(r["object_id"]);g.nodes.setdefault(oid,ProvenanceNode(oid,"object",str(r.get("label",""))))
        for s in r.get("sources",()):
            sid="src:"+str(s);g.nodes.setdefault(sid,ProvenanceNode(sid,"source",str(s)));g.edges.append(ProvenanceEdge(sid,oid,"supports",1.0))
        for ev in r.get("evidence",()):
            eid="ev:"+str(ev.get("id",len(g.edges)));g.nodes.setdefault(eid,ProvenanceNode(eid,"evidence",str(ev.get("kind",""))));g.edges.append(ProvenanceEdge(eid,oid,"supports",float(ev.get("confidence",1.0))))
    return g
