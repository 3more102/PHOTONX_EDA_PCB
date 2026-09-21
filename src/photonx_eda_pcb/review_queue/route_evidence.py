from __future__ import annotations

from collections import Counter

from ..excellon_routing import assess_route_export_readiness, route_export_descriptor
from ..exporters.kicad_policy import kicad_duplicate_object_ids


_REASON_TEXT = {
    "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN": (
        "plated route lacks a source-proven full-stack copper pad-stack with one "
        "unambiguous exported net"
    ),
    "KICAD_PLATED_ROUTE_SPAN_UNPROVEN": (
        "explicit X2 route span is present but is not source-proven"
    ),
    "KICAD_PLATED_ROUTE_PARTIAL_SPAN_UNSUPPORTED": (
        "source-proven partial-depth plated route cannot be represented as a KiCad "
        "through-hole routed slot without widening its span"
    ),
    "KICAD_PLATED_ROUTE_X2_KIND_MISMATCH": (
        "X2 Blind/Buried route kind contradicts the canonical full-stack endpoints"
    ),
    "KICAD_ARBITRARY_ROUTE_UNSUPPORTED": (
        "route is not an exact supported straight non-plated slot or an "
        "evidence-complete full-stack plated routed slot"
    ),
    "KICAD_OBJECT_ID_DUPLICATE": (
        "route object ID is duplicated in the physical board model; deterministic "
        "KiCad identity would be ambiguous"
    ),
}


def _span_text(route) -> str:
    span = getattr(route, "layer_span", None)
    if isinstance(span, (list, tuple)) and len(span) == 2:
        return f"{span[0]} -> {span[1]}"

    x2_span = getattr(route, "x2_layer_span", None)
    if isinstance(x2_span, (list, tuple)) and len(x2_span) == 2:
        return f"X2 {x2_span[0]} -> {x2_span[1]}"
    return "—"


def _net_text(board, net_id):
    if net_id is None:
        return "—"
    matches = [
        net for net in getattr(board, "nets", ()) if str(net.id) == str(net_id)
    ]
    if len(matches) != 1:
        return "<ambiguous>"
    label = getattr(matches[0], "label", None)
    return str(net_id) if label is None else f"{net_id} ({label})"


def build_route_evidence_rows(board) -> list[dict]:
    """Build deterministic route-export evidence rows from the KiCad policy.

    Exportability comes from the same route readiness classifier used by the
    exporter. Global duplicate object IDs are overlaid from the shared KiCad
    identity policy because those objects are omitted before UUID generation.
    """

    routes = sorted(
        getattr(board, "routes", ()),
        key=lambda item: str(getattr(item, "id", "")),
    )
    readiness = assess_route_export_readiness(routes, board)
    exportable = set(str(route_id) for route_id in readiness.exportable)
    duplicate_ids = set(kicad_duplicate_object_ids(board))
    id_counts = Counter(str(getattr(route, "id", "")) for route in routes)

    rows = []
    for index, route in enumerate(routes):
        route_id = str(route.id)
        descriptor = route_export_descriptor(route, board)

        if route_id in duplicate_ids or id_counts[route_id] > 1:
            status = "invalid"
            export_code = "KICAD_OBJECT_ID_DUPLICATE"
            reason = _REASON_TEXT[export_code]
            descriptor = None
        elif route_id in exportable and descriptor is not None:
            status = "exportable"
            export_code = None
            reason = "route is exactly representable by the current KiCad export policy"
        else:
            status = "omitted"
            export_code = readiness.reasons.get(
                route_id,
                "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
            )
            reason = _REASON_TEXT.get(export_code, str(export_code))

        net_id = descriptor.get("net_id") if descriptor is not None else None
        export_kind = descriptor.get("kind") if descriptor is not None else None
        rows.append(
            {
                "id": f"route-evidence:{index}:{route_id}",
                "route_id": route_id,
                "status": status,
                "plating": str(getattr(route, "plated", "unknown")),
                "span": _span_text(route),
                "span_proven": getattr(route, "span_proven", False) is True,
                "x2_kind": str(getattr(route, "x2_span_kind", None) or "—"),
                "width_mm": getattr(route, "width_mm", None),
                "segments": len(getattr(route, "segments", ())),
                "net_id": net_id,
                "net": _net_text(board, net_id),
                "export_kind": export_kind,
                "export_code": export_code,
                "reason": reason,
            }
        )

    return rows
