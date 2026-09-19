from __future__ import annotations

import json
import tkinter as tk

from .state import ViewState


class Inspector(tk.Text):
    def __init__(self, master, state: ViewState, **kwargs):
        super().__init__(master, width=46, **kwargs)
        self.state = state
        self.show(None)

    def show(self, object_id: str | None):
        self.configure(state="normal")
        self.delete("1.0", "end")

        if object_id is None:
            self.insert(
                "end",
                "Select a pad, track, drill, region, route, slot, or outline segment.\n"
                "Selecting a connected object also highlights its reconstructed net.\n",
            )
        else:
            payload = self.state.inspection_payload(object_id)
            self.insert("end", json.dumps(payload, indent=2, default=str))

        self.configure(state="disabled")
