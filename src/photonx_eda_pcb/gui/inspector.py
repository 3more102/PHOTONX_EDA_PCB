from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict, is_dataclass

from .state import ViewState


class Inspector(tk.Text):
    def __init__(self, master, state: ViewState, **kwargs):
        super().__init__(master, width=42, **kwargs)
        self.state = state
        self.show(None)

    def show(self, object_id: str | None):
        self.configure(state="normal")
        self.delete("1.0", "end")
        if object_id is None:
            self.insert(
                "end",
                "Select a track, pad, drill, slot, route, copper region, "
                "or outline segment.\n",
            )
        else:
            obj = self.state.board.object_index().get(object_id)
            payload = (
                asdict(obj)
                if obj is not None and is_dataclass(obj)
                else {"id": object_id, "status": "not found"}
            )
            self.insert("end", json.dumps(payload, indent=2, default=str))
        self.configure(state="disabled")
