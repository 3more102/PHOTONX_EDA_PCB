from __future__ import annotations

import tkinter as tk

from .state import ViewState
from .viewport import board_bounds, fit_view, zoom_about


class BoardCanvas(tk.Canvas):
    def __init__(self, master, state: ViewState, on_select=None, **kwargs):
        super().__init__(master, background="white", **kwargs)
        self.state = state
        self.on_select = on_select
        self._pan_anchor = None
        self.bind("<Button-1>", self._click)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-4>", self._wheel_linux)
        self.bind("<Button-5>", self._wheel_linux)
        self.bind("<ButtonPress-2>", self._pan_start)
        self.bind("<B2-Motion>", self._pan_move)
        self.bind("<Configure>", lambda _e: self.redraw())
        self.redraw()

    def xy(self, x, y):
        s = self.state.scale
        return self.state.offset_x + x * s, self.state.offset_y + y * s

    def fit_to_board(self):
        scale, offset_x, offset_y = fit_view(
            board_bounds(self.state.board),
            self.winfo_width(),
            self.winfo_height(),
        )
        self.state.scale = scale
        self.state.offset_x = offset_x
        self.state.offset_y = offset_y
        self.redraw()

    def redraw(self):
        self.delete("all")
        board = self.state.board
        highlighted = self.state.highlighted_net_id

        for region in board.regions:
            coords = [value for point in region.points for value in self.xy(point.x, point.y)]
            if len(coords) >= 6:
                stipple = "gray50" if highlighted in {None, region.net_id} else "gray75"
                self.create_polygon(
                    *coords,
                    fill="black",
                    outline="black",
                    stipple=stipple,
                    width=1,
                    tags=(region.id, "region"),
                )
                for hole in region.holes:
                    hole_coords = [value for point in hole for value in self.xy(point.x, point.y)]
                    if len(hole_coords) >= 6:
                        self.create_polygon(
                            *hole_coords,
                            fill="white",
                            outline="black",
                            width=1,
                            tags=(region.id, "region-hole"),
                        )

        for track in board.tracks:
            x1, y1 = self.xy(track.start.x, track.start.y)
            x2, y2 = self.xy(track.end.x, track.end.y)
            width = max(2, track.width * self.state.scale)
            dash = () if highlighted in {None, track.net_id} else (2, 3)
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

        for route in board.routes:
            coords = [value for point in route.points for value in self.xy(point[0], point[1])]
            if len(coords) >= 4:
                self.create_line(
                    *coords,
                    width=max(2, route.width_mm * self.state.scale),
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                    tags=(route.id, "route"),
                )

        for slot in board.slots:
            x1, y1 = self.xy(slot.start[0], slot.start[1])
            x2, y2 = self.xy(slot.end[0], slot.end[1])
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=max(2, slot.width_mm * self.state.scale),
                capstyle=tk.ROUND,
                tags=(slot.id, "slot"),
            )

        for pad in board.pads:
            x, y = self.xy(pad.center.x, pad.center.y)
            rx = pad.size_x * self.state.scale / 2
            ry = pad.size_y * self.state.scale / 2
            stipple = "" if highlighted in {None, pad.net_id} else "gray50"
            self.create_oval(
                x - rx,
                y - ry,
                x + rx,
                y + ry,
                width=2,
                stipple=stipple,
                tags=(pad.id, "pad"),
            )

        for drill in board.drills:
            x, y = self.xy(drill.center.x, drill.center.y)
            radius = drill.diameter * self.state.scale / 2
            self.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="white",
                width=2,
                tags=(drill.id, "drill"),
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

        if self.state.selected_id:
            for item in self.find_withtag(self.state.selected_id):
                self.itemconfigure(item, width=4)

    def _click(self, event):
        items = self.find_overlapping(event.x - 3, event.y - 3, event.x + 3, event.y + 3)
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
        self._zoom(event.x, event.y, factor)

    def _wheel_linux(self, event):
        factor = 1.15 if event.num == 4 else 1 / 1.15
        self._zoom(event.x, event.y, factor)

    def _zoom(self, x, y, factor):
        scale, offset_x, offset_y = zoom_about(
            self.state.scale,
            self.state.offset_x,
            self.state.offset_y,
            x,
            y,
            factor,
        )
        self.state.scale = scale
        self.state.offset_x = offset_x
        self.state.offset_y = offset_y
        self.redraw()

    def _pan_start(self, event):
        self._pan_anchor = (
            event.x,
            event.y,
            self.state.offset_x,
            self.state.offset_y,
        )

    def _pan_move(self, event):
        if self._pan_anchor is None:
            return
        start_x, start_y, offset_x, offset_y = self._pan_anchor
        self.state.offset_x = offset_x + (event.x - start_x)
        self.state.offset_y = offset_y + (event.y - start_y)
        self.redraw()
