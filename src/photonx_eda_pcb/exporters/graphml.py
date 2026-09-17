from pathlib import Path
from xml.etree.ElementTree import Element,SubElement,ElementTree
def export_graphml(board,path:str|Path)->Path:
    root=Element("graphml",xmlns="http://graphml.graphdrawing.org/xmlns"); graph=SubElement(root,"graph",edgedefault="undirected",id="G")
    members=set(m for n in board.nets for m in n.members)
    for m in sorted(members): SubElement(graph,"node",id=m)
    edge_id=0
    for n in board.nets:
        if not n.members: continue
        anchor=n.members[0]
        for member in n.members[1:]: SubElement(graph,"edge",id=f"e{edge_id}",source=anchor,target=member); edge_id+=1
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); ElementTree(root).write(path,encoding="utf-8",xml_declaration=True); return path
