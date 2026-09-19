from __future__ import annotations

import tkinter as tk

from .confidence import confidence_color, net_confidence
from .state import ViewState


class BoardCanvas(tk.Canvas):
    def __init__(self, master, state: ViewState, on_select=None, **kwargs):
        super().__init__(master, background="white", **kwargs)
        self.state = state
        self.on_select = on_select
        self.bind("<Button-1>", self._click)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Configure>", lambda _e: self.redraw())
        self.redraw()

    def xy(self, x, y):
        s = self.state.scale
        return self.state.offset_x + x * s, self.state.offset_y + y * s

    def _object_color(self, net_id: str | None) -> str:
        if not self.state.show_confidence_heatmap:
            return "black"
        return confidence_color(net_confidence(self.state.board, net_id))

    def _draw_confidence_legend(self) -> None:
        if not self.state.show_confidence_heatmap:
            return
        entries = (
            ("High >= 0.90", confidence_color(0.90)),
            ("Medium >= 0.70", confidence_color(0.70)),
            ("Low < 0.70", confidence_color(0.69)),
            ("Unknown", confidence_color(None)),
        )
        x0, y0 = 10, 10
        self.create_rectangle(
            x0 - 6,
            y0 - 6,
            x0 + 144,
            y0 + 18 * len(entries) + 6,
            fill="white",
            outline="#dadce0",
            tags=("confidence_legend",),
        )
        for index, (label, color) in enumerate(entries):
            y = y0 + index * 18
            self.create_rectangle(
                x0,
                y,
                x0 + 12,
                y + 12,
                fill=color,
                outline=color,
                tags=("confidence_legend",),
            )
            self.create_text(
                x0 + 18,
                y + 6,
                text=label,
                anchor="w",
                fill="black",
                tags=("confidence_legend",),
            )

    def redraw(self):
        self.delete("all")
        board = self.state.board
        highlighted = self.state.highlighted_net_id

        for seg in board.outline:
            x1, y1 = self.xy(seg.start.x, seg.start.y)
            x2, y2 = self.xy(seg.end.x, seg.end.y)
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=2,
                fill="#5f6368" if self.state.show_confidence_heatmap else "black",
                tags=(seg.id, "outline"),
            )

        for trk in board.tracks:
            x1, y1 = self.xy(trk.start.x, trk.start.y)
            x2, y2 = self.xy(trk.end.x, trk.end.y)
            width = max(2, trk.width * self.state.scale)
            dash = () if highlighted in {None, trk.net_id} else (2, 3)
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=width,
                capstyle=tk.ROUND,
                dash=dash,
                fill=self._object_color(trk.net_id),
                tags=(trk.id, "track"),
            )

        for pad in board.pads:
            x, y = self.xy(pad.center.x, pad.center.y)
            rx = pad.size_x * self.state.scale / 2
            ry = pad.size_y * self.state.scale / 2
            stipple = "" if highlighted in {None, pad.net_id} else "gray50"
            color = self._object_color(pad.net_id)
            self.create_oval(
                x - rx,
                y - ry,
                x + rx,
                y + ry,
                width=2,
                outline=color,
                fill=color if self.state.show_confidence_heatmap else "",
                stipple=stipple,
                tags=(pad.id, "pad"),
            )

        if self.state.selected_id:
            for item in self.find_withtag(self.state.selected_id):
                self.itemconfigure(item, width=4)

        self._draw_confidence_legend()

    def _click(self, event):
        items = self.find_overlapping(event.x - 3, event.y - 3, event.x + 3, event.y + 3)
        selected = None
        if items:
            tags = self.gettags(items[-1])
            selected = tags[0] if tags and tags[0] != "confidence_legend" else None
        self.state.selected_id = selected
        if self.on_select:
            self.on_select(selected)
        self.redraw()

    def _wheel(self, event):
        factor = 1.15 if event.delta > 0 else 1 / 1.15
        self.state.scale = min(100.0, max(2.0, self.state.scale * factor))
        self.redraw()
