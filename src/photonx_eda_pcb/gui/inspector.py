from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict, is_dataclass

from ..via_review import via_review_descriptor
from .state import ViewState


def _find_entity(state: ViewState, object_id: str):
    board = state.board
    obj = board.object_index().get(object_id)
    if obj is not None:
        return obj
    for item in (*board.nets, *board.components):
        if item.id == object_id:
            return item
    return None


class Inspector(tk.Text):
    def __init__(self, master, state: ViewState, **kwargs):
        super().__init__(master, width=42, **kwargs)
        self.state = state
        self.show(None)

    def _show_payload(self, payload) -> None:
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", json.dumps(payload, indent=2, default=str))
        self.configure(state="disabled")

    def show(self, object_id: str | None):
        if object_id is None:
            self.configure(state="normal")
            self.delete("1.0", "end")
            self.insert(
                "end",
                "Select a board object, physical net, component hypothesis, "
                "or review item.\n",
            )
            self.configure(state="disabled")
            return

        obj = _find_entity(self.state, object_id)
        payload = (
            asdict(obj)
            if obj is not None and is_dataclass(obj)
            else {"id": object_id, "status": "not found"}
        )

        via = via_review_descriptor(self.state.board, object_id)
        if via is not None:
            payload = dict(payload)
            payload["via_review"] = asdict(via)

        self._show_payload(payload)

    def show_review(self, item) -> None:
        payload = asdict(item) if is_dataclass(item) else {"review": str(item)}
        self._show_payload(payload)
