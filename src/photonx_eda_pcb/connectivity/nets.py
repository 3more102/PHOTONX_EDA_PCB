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


def _plated_via_evidence(
    board: BoardModel,
    graph: nx.Graph,
    members: list[str],
) -> tuple[list[Evidence], list[object]]:
    by_drill: dict[str, dict[str, object]] = {}
    for left_id, right_id, data in graph.subgraph(members).edges(data=True):
        if data.get("reason") != "plated_via_span":
            continue
        drill_id = str(data.get("drill_id") or "")
        if not drill_id:
            continue
        entry = by_drill.setdefault(
            drill_id,
            {
                "pads": set(),
                "from_layer": data.get("from_layer"),
                "to_layer": data.get("to_layer"),
                "confidence": float(data.get("confidence", 0.0)),
            },
        )
        entry["pads"].update((left_id, right_id))
        entry["confidence"] = min(
            float(entry["confidence"]),
            float(data.get("confidence", 0.0)),
        )

    index = board.object_index()
    evidence: list[Evidence] = []
    sources: list[object] = []
    for drill_id in sorted(by_drill):
        entry = by_drill[drill_id]
        drill = index.get(drill_id)
        source = None
        provenance = getattr(drill, "provenance", None)
        if getattr(provenance, "sources", None):
            source = provenance.sources[0]
            if source not in sources:
                sources.append(source)

        pads = ",".join(sorted(entry["pads"]))
        evidence.append(
            Evidence(
                "plated_via_span",
                (
                    f"drill={drill_id}; "
                    f"span={entry['from_layer']}->{entry['to_layer']}; "
                    f"pads={pads}"
                ),
                float(entry["confidence"]),
                source,
            )
        )
    return evidence, sources


def assign_physical_nets(board: BoardModel, graph: nx.Graph) -> list[NetGroup]:
    index = board.object_index()
    nets = []
    for component in sorted(
        nx.connected_components(graph),
        key=lambda ids: sorted(ids)[0],
    ):
        members = sorted(component)
        net_id = stable_id("net", *members)

        via_evidence, via_sources = _plated_via_evidence(
            board,
            graph,
            members,
        )
        net_confidence = min(
            [0.99, *(item.confidence for item in via_evidence)]
        )
        connectivity_detail = (
            "members connected by copper geometry and evidence-backed plated-via spans"
            if via_evidence
            else "members connected by copper geometry"
        )
        prov = Provenance(
            evidence=[
                Evidence(
                    "connectivity",
                    connectivity_detail,
                    net_confidence,
                )
            ]
        )
        for item in via_evidence:
            prov.add_evidence(item)
        for source in via_sources:
            prov.add_source(source)

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
        elif x2_names == ["N/C"]:
            prov.add_evidence(
                Evidence(
                    "gerber_x2_reserved_nc",
                    "reserved X2 net name N/C is preserved as evidence, not a unique net label",
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

        net = NetGroup(
            net_id,
            members,
            net_confidence,
            label=label,
            provenance=prov,
        )
        nets.append(net)
        for member in members:
            obj = index.get(member)
            if hasattr(obj, "net_id"):
                obj.net_id = net_id

    label_counts: dict[str, int] = {}
    for net in nets:
        if net.label:
            label_counts[net.label] = label_counts.get(net.label, 0) + 1

    for net in nets:
        if net.label and label_counts.get(net.label, 0) > 1:
            duplicate = net.label
            net.label = None
            net.provenance.add_evidence(
                Evidence(
                    "gerber_x2_duplicate_net_label",
                    (
                        f"name={duplicate}; physical_groups={label_counts[duplicate]}; "
                        "label left unresolved"
                    ),
                    1.0,
                )
            )

    board.nets = nets
    return nets
