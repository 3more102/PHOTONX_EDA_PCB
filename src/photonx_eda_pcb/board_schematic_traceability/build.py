from .model import BoardSchematicTrace,BoardSchematicTraceability
def build_board_schematic_traceability(schematic_graph,page_set):
    pages_by_comp={};pages_by_net={}
    for p in page_set.pages:
        for c in p.components:pages_by_comp.setdefault(c,[]).append(p.id)
        for n in p.nets:pages_by_net.setdefault(n,[]).append(p.id)
    traces=[]
    for cid in sorted(schematic_graph.components):
        nets=sorted({n for c,_,n in schematic_graph.pin_edges if c==cid})
        traces.append(BoardSchematicTrace("component",cid,tuple(sorted(pages_by_comp.get(cid,()))),tuple(nets),(cid,)))
    for nid in sorted(schematic_graph.nets):
        comps=sorted({c for c,_,n in schematic_graph.pin_edges if n==nid})
        traces.append(BoardSchematicTrace("net",nid,tuple(sorted(pages_by_net.get(nid,()))),(nid,),tuple(comps)))
    return BoardSchematicTraceability(traces)
