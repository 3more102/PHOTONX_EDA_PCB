from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass

from ..models import BoardModel, NetGroup


@dataclass
class ViewState:
    board: BoardModel
    selected_id: str | None = None
    highlighted_net_id: str | None = None
    scale: float = 12.0
    offset_x: float = 30.0
    offset_y: float = 30.0

    def object_by_id(self, object_id: str | None):
        if object_id is None:
            return None
        return self.board.object_index().get(object_id)

    def net_by_id(self, net_id: str | None) -> NetGroup | None:
        if net_id is None:
            return None
        return next((net for net in self.board.nets if net.id == net_id), None)

    def net_for_object(self, object_id: str | None) -> NetGroup | None:
        obj = self.object_by_id(object_id)
        if obj is None:
            return None

        direct_net_id = getattr(obj, "net_id", None)
        if direct_net_id:
            direct = self.net_by_id(direct_net_id)
            if direct is not None:
                return direct

        return next(
            (net for net in self.board.nets if object_id in net.members),
            None,
        )

    def select(self, object_id: str | None, *, sync_net: bool = True) -> str | None:
        if object_id is not None and self.object_by_id(object_id) is None:
            object_id = None

        self.selected_id = object_id
        if sync_net:
            net = self.net_for_object(object_id)
            self.highlighted_net_id = net.id if net is not None else None
        return self.selected_id

    def highlight_net(self, net_id: str | None) -> str | None:
        self.highlighted_net_id = net_id if self.net_by_id(net_id) is not None else None
        return self.highlighted_net_id

    def inspection_payload(self, object_id: str | None) -> dict[str, object]:
        obj = self.object_by_id(object_id)
        if obj is None:
            return {
                "id": object_id,
                "status": "not found",
                "resolved_net": None,
            }

        if is_dataclass(obj):
            object_payload: object = asdict(obj)
        else:
            object_payload = {"id": object_id, "repr": repr(obj)}

        net = self.net_for_object(object_id)
        net_payload = None
        if net is not None:
            net_payload = {
                "id": net.id,
                "label": net.label,
                "confidence": net.confidence,
                "member_count": len(net.members),
            }

        provenance = getattr(obj, "provenance", None)
        evidence_summary = None
        if provenance is not None:
            evidence = list(getattr(provenance, "evidence", []))
            evidence_summary = {
                "source_count": len(getattr(provenance, "sources", [])),
                "evidence_count": len(evidence),
                "max_confidence": max(
                    (item.confidence for item in evidence),
                    default=None,
                ),
            }

        return {
            "id": object_id,
            "object_type": type(obj).__name__,
            "object": object_payload,
            "resolved_net": net_payload,
            "evidence_summary": evidence_summary,
        }
