from collections.abc import Mapping


def route_omission_manifest(board):
    routes = getattr(board, "routes", ())
    return {
        "omitted_routes": [r.id for r in routes],
        "reasons": {
            r.id: "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
            for r in routes
        },
    }


def _append_once(issues, code):
    if code not in issues:
        issues.append(code)


def validate_route_omission_manifest(data):
    """Validate a route-omission manifest without trusting its decoded shape.

    Manifests can be loaded from JSON or other external artifacts, so malformed
    containers and identifiers must produce deterministic validation findings
    rather than exceptions.
    """
    if not isinstance(data, Mapping):
        return ["ROUTE_OMISSION_MANIFEST_INVALID"]

    issues = []

    raw_ids = data.get("omitted_routes", ())
    if not isinstance(raw_ids, (list, tuple)):
        _append_once(issues, "ROUTE_OMISSION_IDS_INVALID")
        ids = []
    else:
        ids = []
        seen = set()
        duplicate = False
        for rid in raw_ids:
            if not isinstance(rid, str) or not rid.strip():
                _append_once(issues, "ROUTE_OMISSION_ID_INVALID")
                continue
            ids.append(rid)
            if rid in seen:
                duplicate = True
            else:
                seen.add(rid)
        if duplicate:
            _append_once(issues, "ROUTE_OMISSION_DUPLICATE_ID")

    raw_reasons = data.get("reasons", {})
    if not isinstance(raw_reasons, Mapping):
        _append_once(issues, "ROUTE_OMISSION_REASONS_INVALID")
        reasons = {}
    else:
        reasons = raw_reasons
        for rid, reason in reasons.items():
            if not isinstance(rid, str) or not rid.strip():
                _append_once(issues, "ROUTE_OMISSION_REASON_ID_INVALID")
            if not isinstance(reason, str) or not reason.strip():
                _append_once(issues, "ROUTE_OMISSION_REASON_INVALID")

    valid_ids = set(ids)
    for rid in dict.fromkeys(ids):
        if rid not in reasons:
            _append_once(issues, "ROUTE_OMISSION_WITHOUT_REASON")

    for rid in reasons:
        if isinstance(rid, str) and rid.strip() and rid not in valid_ids:
            _append_once(issues, "ROUTE_OMISSION_REASON_WITHOUT_ROUTE")

    return issues
