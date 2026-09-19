from __future__ import annotations
import networkx as nx
from ..ids import stable_id
from ..models import BoardModel, NetGroup
from ..provenance import Evidence, Provenance


def _x2_net_evidence(index: dict[str, object], members: list[str]) -> list[Evidence]:
    evidence: list[Evidence] = []
    for member in members:
        obj = index.get(member)
        provenance = getattr(obj, "provenance", None)
        for item in getattr(provenance, "evidence", ()):
            if item.kind == "gerber_x2_net_name":
                evidence.append(item)
    return evidence


def assign_physical_nets(board: BoardModel, graph: nx.Graph) -> list[NetGroup]:
    index = board.object_index(); nets = []
    for component in sorted(nx.connected_components(graph), key=lambda ids: sorted(ids)[0]):
        members = sorted(component); net_id = stable_id("net", *members)
        prov = Provenance(evidence=[Evidence("connectivity", "members connected by copper geometry", 0.99)])

        x2_evidence = _x2_net_evidence(index, members)
        x2_names = sorted({item.detail for item in x2_evidence})
        for item in x2_evidence:
            if item.source is not None:
                prov.add_source(item.source)

        label = None
        if x2_names == [""]:
            prov.add_evidence(
                Evidence(
                    "gerber_x2_no_net",
                    "all explicit X2 .N evidence identifies no connected CAD net",
                    1.0,
                )
            )
        elif len(x2_names) == 1:
            label = x2_names[0]
            prov.add_evidence(
                Evidence(
                    "gerber_x2_net_label",
                    f"name={label}",
                    0.99,
                )
            )
        elif len(x2_names) > 1:
            prov.add_evidence(
                Evidence(
                    "gerber_x2_net_name_conflict",
                    f"names={x2_names!r}",
                    1.0,
                )
            )

        net = NetGroup(net_id, members, 0.99, label=label, provenance=prov); nets.append(net)
        for member in members:
            obj = index.get(member)
            if hasattr(obj, "net_id"): obj.net_id = net_id
    board.nets = nets; return nets
