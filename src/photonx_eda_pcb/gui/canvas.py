from __future__ import annotations

import tkinter as tk

from .state import EDGE_CUTS_LAYER, ViewState


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
        scale = self.state.scale
        return (
            self.state.offset_x + x * scale,
            self.state.offset_y + y * scale,
        )

    @staticmethod
    def _deemphasized(highlighted: str | None, net_id: str | None) -> bool:
        return highlighted is not None and highlighted != net_id

    def _draw_region(self, region, highlighted: str | None) -> None:
        if len(region.points) < 3:
            return
        shell = []
        for point in region.points:
            shell.extend(self.xy(point.x, point.y))
        dash = (2, 3) if self._deemphasized(highlighted, region.net_id) else ()
        self.create_polygon(
            *shell,
            fill="",
            outline="black",
            width=2,
            dash=dash,
            tags=(region.id, "region"),
        )
        for hole in region.holes:
            if len(hole) < 3:
                continue
            coords = []
            for point in hole:
                coords.extend(self.xy(point.x, point.y))
            self.create_polygon(
                *coords,
                fill="",
                outline="black",
                width=1,
                dash=(3, 3),
                tags=(region.id, "region-hole"),
            )

    def redraw(self):
        self.delete("all")
        board = self.state.board
        highlighted = self.state.highlighted_net_id

        if self.state.is_layer_visible(EDGE_CUTS_LAYER):
            for seg in board.outline:
                x1, y1 = self.xy(seg.start.x, seg.start.y)
                x2, y2 = self.xy(seg.end.x, seg.end.y)
                self.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    width=2,
                    tags=(seg.id, "outline"),
                )

        for region in board.regions:
            if self.state.is_layer_visible(region.layer):
                self._draw_region(region, highlighted)

        for track in board.tracks:
            if not self.state.is_layer_visible(track.layer):
                continue
            x1, y1 = self.xy(track.start.x, track.start.y)
            x2, y2 = self.xy(track.end.x, track.end.y)
            width = max(2, track.width * self.state.scale)
            dash = (2, 3) if self._deemphasized(highlighted, track.net_id) else ()
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=width,
                capstyle=tk.ROUND,
                dash=dash,
                tags=(track.id, "track"),
            )

        for pad in board.pads:
            if not self.state.is_layer_visible(pad.layer):
                continue
            x, y = self.xy(pad.center.x, pad.center.y)
            rx = pad.size_x * self.state.scale / 2
            ry = pad.size_y * self.state.scale / 2
            stipple = (
                "gray50"
                if self._deemphasized(highlighted, pad.net_id)
                else ""
            )
            self.create_oval(
                x - rx,
                y - ry,
                x + rx,
                y + ry,
                width=2,
                stipple=stipple,
                tags=(pad.id, "pad"),
            )

        if self.state.selected_id:
            for item in self.find_withtag(self.state.selected_id):
                self.itemconfigure(item, width=4)

    def _click(self, event):
        items = self.find_overlapping(
            event.x - 3,
            event.y - 3,
            event.x + 3,
            event.y + 3,
        )
        selected = None
        if items:
            tags = self.gettags(items[-1])
            selected = tags[0] if tags else None
        self.state.selected_id = selected
        if self.on_select:
            self.on_select(selected)
        self.redraw()

    def _wheel(self, event):
        factor = 1.15 if event.delta > 0 else 1 / 1.15
        self.state.scale = min(
            100.0,
            max(2.0, self.state.scale * factor),
        )
        self.redraw()
