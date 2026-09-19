from __future__ import annotations


def canonical_board_dict(board):
    def pt(p):
        return [round(float(p.x), 6), round(float(p.y), 6)]

    def xy(p):
        return [round(float(p[0]), 6), round(float(p[1]), 6)]

    def slot(s):
        return {
            "id": s.id,
            "start": xy(s.start),
            "end": xy(s.end),
            "width_mm": round(float(s.width_mm), 6),
            "plated": s.plated,
            "tool": s.tool,
        }

    def route(r):
        return {
            "id": r.id,
            "points": [xy(p) for p in r.points],
            "width_mm": round(float(r.width_mm), 6),
            "plated": r.plated,
            "tool": r.tool,
        }

    def component(c):
        return {
            "id": c.id,
            "pad_ids": sorted(c.pad_ids),
            "kind": c.kind,
            "confidence": round(float(c.confidence), 6),
            "evidence": list(c.evidence),
            "reference": c.reference,
        }

    return {
        "tracks": sorted(
            [
                {
                    "id": x.id,
                    "start": pt(x.start),
                    "end": pt(x.end),
                    "width": round(float(x.width), 6),
                    "layer": x.layer,
                    "net_id": x.net_id,
                }
                for x in board.tracks
            ],
            key=lambda x: x["id"],
        ),
        "pads": sorted(
            [
                {
                    "id": x.id,
                    "center": pt(x.center),
                    "size": [round(float(x.size_x), 6), round(float(x.size_y), 6)],
                    "shape": x.shape,
                    "layer": x.layer,
                    "drill": None if x.drill is None else round(float(x.drill), 6),
                    "net_id": x.net_id,
                }
                for x in board.pads
            ],
            key=lambda x: x["id"],
        ),
        "drills": sorted(
            [
                {
                    "id": x.id,
                    "center": pt(x.center),
                    "diameter": round(float(x.diameter), 6),
                    "plating": x.plating,
                }
                for x in board.drills
            ],
            key=lambda x: x["id"],
        ),
        "slots": sorted(
            [slot(x) for x in getattr(board, "slots", ())],
            key=lambda x: x["id"],
        ),
        "routes": sorted(
            [route(x) for x in getattr(board, "routes", ())],
            key=lambda x: x["id"],
        ),
        "regions": sorted(
            [
                {
                    "id": x.id,
                    "points": [pt(p) for p in x.points],
                    "holes": [[pt(p) for p in ring] for ring in getattr(x, "holes", ())],
                    "layer": x.layer,
                    "net_id": x.net_id,
                }
                for x in getattr(board, "regions", ())
            ],
            key=lambda x: x["id"],
        ),
        "outline": sorted(
            [{"id": x.id, "start": pt(x.start), "end": pt(x.end)} for x in board.outline],
            key=lambda x: x["id"],
        ),
        "nets": sorted(
            [
                {
                    "id": x.id,
                    "members": sorted(x.members),
                    "label": x.label,
                }
                for x in board.nets
            ],
            key=lambda x: x["id"],
        ),
        "components": sorted(
            [component(x) for x in board.components],
            key=lambda x: x["id"],
        ),
    }
