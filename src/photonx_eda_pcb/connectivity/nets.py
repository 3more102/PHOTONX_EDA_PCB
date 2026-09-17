from __future__ import annotations
import networkx as nx
from ..ids import stable_id
from ..models import BoardModel, NetGroup
from ..provenance import Evidence, Provenance


def assign_physical_nets(board: BoardModel, graph: nx.Graph) -> list[NetGroup]:
    index = board.object_index(); nets = []
    for component in sorted(nx.connected_components(graph), key=lambda ids: sorted(ids)[0]):
        members = sorted(component); net_id = stable_id("net", *members)
        prov = Provenance(evidence=[Evidence("connectivity", "members connected by copper geometry", 0.99)])
        net = NetGroup(net_id, members, 0.99, label=None, provenance=prov); nets.append(net)
        for member in members:
            obj = index.get(member)
            if hasattr(obj, "net_id"): obj.net_id = net_id
    board.nets = nets; return nets
