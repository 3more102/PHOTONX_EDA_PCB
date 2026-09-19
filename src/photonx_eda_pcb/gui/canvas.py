from __future__ import annotations

import tkinter as tk

from .state import ViewState
from .viewport import fit_viewport


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
        return self.state.offset_x + x * scale, self.state.offset_y + y * scale

    def _dimmed(self, net_id: str | None) -> bool:
        highlighted = self.state.highlighted_net_id
        return highlighted is not None and highlighted != net_id

    def redraw(self):
        self.delete("all")
        board = self.state.board

        for region in board.regions:
            coords = []
            for point in region.points:
                coords.extend(self.xy(point.x, point.y))
            if len(coords) >= 6:
                self.create_polygon(
                    *coords,
                    fill="",
                    width=2,
                    dash=(2, 3) if self._dimmed(region.net_id) else (),
                    tags=(region.id, "region"),
                )
            for hole in region.holes:
                hole_coords = []
                for point in hole:
                    hole_coords.extend(self.xy(point.x, point.y))
                if len(hole_coords) >= 4:
                    self.create_line(
                        *hole_coords,
                        *hole_coords[:2],
                        width=1,
                        dash=(2, 2),
                        tags=(region.id, "region-hole"),
                    )

        for segment in board.outline:
            x1, y1 = self.xy(segment.start.x, segment.start.y)
            x2, y2 = self.xy(segment.end.x, segment.end.y)
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=2,
                tags=(segment.id, "outline"),
            )

        for route in board.routes:
            coords = []
            for x, y in route.points:
                coords.extend(self.xy(x, y))
            if len(coords) >= 4:
                self.create_line(
                    *coords,
                    width=max(2, route.width_mm * self.state.scale),
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                    dash=(6, 3),
                    tags=(route.id, "route"),
                )

        for slot in board.slots:
            x1, y1 = self.xy(*slot.start)
            x2, y2 = self.xy(*slot.end)
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=max(2, slot.width_mm * self.state.scale),
                capstyle=tk.ROUND,
                dash=(4, 2),
                tags=(slot.id, "slot"),
            )

        for track in board.tracks:
            x1, y1 = self.xy(track.start.x, track.start.y)
            x2, y2 = self.xy(track.end.x, track.end.y)
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=max(2, track.width * self.state.scale),
                capstyle=tk.ROUND,
                dash=(2, 3) if self._dimmed(track.net_id) else (),
                tags=(track.id, "track"),
            )

        for pad in board.pads:
            x, y = self.xy(pad.center.x, pad.center.y)
            rx = pad.size_x * self.state.scale / 2
            ry = pad.size_y * self.state.scale / 2
            self.create_oval(
                x - rx,
                y - ry,
                x + rx,
                y + ry,
                width=2,
                stipple="gray50" if self._dimmed(pad.net_id) else "",
                tags=(pad.id, "pad"),
            )

        for drill in board.drills:
            x, y = self.xy(drill.center.x, drill.center.y)
            radius = max(2.0, drill.diameter * self.state.scale / 2)
            tags = (drill.id, "drill")
            self.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                width=2,
                tags=tags,
            )
            cross = min(radius * 0.65, 8.0)
            self.create_line(x - cross, y, x + cross, y, tags=tags)
            self.create_line(x, y - cross, x, y + cross, tags=tags)

        if self.state.selected_id:
            for item in self.find_withtag(self.state.selected_id):
                self.itemconfigure(item, width=4)

    def fit_to_board(self):
        fitted = fit_viewport(
            self.state.board,
            max(1, self.winfo_width()),
            max(1, self.winfo_height()),
        )
        if fitted is None:
            return
        self.state.scale, self.state.offset_x, self.state.offset_y = fitted
        self.redraw()

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
        self.state.scale = min(100.0, max(0.05, self.state.scale * factor))
        self.redraw()
