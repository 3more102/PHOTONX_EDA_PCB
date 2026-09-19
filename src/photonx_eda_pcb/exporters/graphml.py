from pathlib import Path
from xml.etree.ElementTree import Element,ElementTree,SubElement


def _canonical_nets(board):
    return sorted(
        board.nets,
        key=lambda net: (str(net.id), tuple(sorted(str(member) for member in net.members))),
    )


def export_graphml(board,path:str|Path)->Path:
    root=Element("graphml",xmlns="http://graphml.graphdrawing.org/xmlns"); graph=SubElement(root,"graph",edgedefault="undirected",id="G")
    members={member for net in board.nets for member in net.members}
    for member in sorted(members): SubElement(graph,"node",id=member)
    edge_id=0
    for net in _canonical_nets(board):
        ordered_members=sorted(net.members)
        if not ordered_members: continue
        anchor=ordered_members[0]
        for member in ordered_members[1:]: SubElement(graph,"edge",id=f"e{edge_id}",source=anchor,target=member); edge_id+=1
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); ElementTree(root).write(path,encoding="utf-8",xml_declaration=True); return path
