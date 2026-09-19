from __future__ import annotations

import tkinter as tk

from .state import ViewState


class BoardCanvas(tk.Canvas):
    def __init__(self, master, state: ViewState, on_select=None, **kwargs):
        super().__init__(master, background="white", **kwargs)
        self.state = state
        self.on_select = on_select
        self._pan_anchor: tuple[int, int] | None = None

        self.bind("<Button-1>", self._click)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-4>", lambda event: self._wheel_steps(event, 1))
        self.bind("<Button-5>", lambda event: self._wheel_steps(event, -1))
        self.bind("<ButtonPress-2>", self._pan_start)
        self.bind("<B2-Motion>", self._pan_move)
        self.bind("<Configure>", lambda _event: self.redraw())
        self.redraw()

    def xy(self, x, y):
        scale = self.state.scale
        return (
            self.state.offset_x + x * scale,
            self.state.offset_y + y * scale,
        )

    def _net_dimmed(self, net_id: str | None) -> bool:
        highlighted = self.state.highlighted_net_id
        return highlighted is not None and highlighted != net_id

    def redraw(self):
        self.delete("all")
        board = self.state.board

        for region in board.regions:
            points = [
                coord
                for point in region.points
                for coord in self.xy(point.x, point.y)
            ]
            if len(points) >= 6:
                dash = (2, 3) if self._net_dimmed(region.net_id) else ()
                self.create_polygon(
                    points,
                    fill="",
                    width=2,
                    dash=dash,
                    tags=(region.id, "region"),
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
            points = [
                coord
                for point in route.points
                for coord in self.xy(point[0], point[1])
            ]
            if len(points) >= 4:
                self.create_line(
                    *points,
                    width=max(2, route.width_mm * self.state.scale),
                    dash=(5, 3),
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
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
                tags=(slot.id, "slot"),
            )

        for track in board.tracks:
            x1, y1 = self.xy(track.start.x, track.start.y)
            x2, y2 = self.xy(track.end.x, track.end.y)
            dash = (2, 3) if self._net_dimmed(track.net_id) else ()
            self.create_line(
                x1,
                y1,
                x2,
                y2,
                width=max(2, track.width * self.state.scale),
                capstyle=tk.ROUND,
                dash=dash,
                tags=(track.id, "track"),
            )

        for drill in board.drills:
            x, y = self.xy(drill.center.x, drill.center.y)
            radius = drill.diameter * self.state.scale / 2
            self.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                width=2,
                tags=(drill.id, "drill"),
            )

        for pad in board.pads:
            x, y = self.xy(pad.center.x, pad.center.y)
            radius_x = pad.size_x * self.state.scale / 2
            radius_y = pad.size_y * self.state.scale / 2
            stipple = "gray50" if self._net_dimmed(pad.net_id) else ""
            self.create_oval(
                x - radius_x,
                y - radius_y,
                x + radius_x,
                y + radius_y,
                width=2,
                stipple=stipple,
                tags=(pad.id, "pad"),
            )

        self._draw_selection()

    def _draw_selection(self):
        if self.state.selected_id is None:
            return

        bounds = self.bbox(self.state.selected_id)
        if bounds is None:
            return

        x1, y1, x2, y2 = bounds
        padding = 4
        self.create_rectangle(
            x1 - padding,
            y1 - padding,
            x2 + padding,
            y2 + padding,
            width=2,
            dash=(4, 2),
            tags=("selection",),
        )

    def _click(self, event):
        items = self.find_overlapping(
            event.x - 3,
            event.y - 3,
            event.x + 3,
            event.y + 3,
        )
        selected = None
        for item in reversed(items):
            tags = self.gettags(item)
            candidate = tags[0] if tags else None
            if candidate and candidate != "selection":
                selected = candidate
                break

        self.state.select(selected, sync_net=True)
        if self.on_select:
            self.on_select(self.state.selected_id)
        self.redraw()

    def _zoom_at(self, x: float, y: float, factor: float):
        old_scale = self.state.scale
        new_scale = min(100.0, max(2.0, old_scale * factor))
        if new_scale == old_scale:
            return

        world_x = (x - self.state.offset_x) / old_scale
        world_y = (y - self.state.offset_y) / old_scale
        self.state.scale = new_scale
        self.state.offset_x = x - world_x * new_scale
        self.state.offset_y = y - world_y * new_scale
        self.redraw()

    def _wheel(self, event):
        self._zoom_at(
            event.x,
            event.y,
            1.15 if event.delta > 0 else 1 / 1.15,
        )

    def _wheel_steps(self, event, steps: int):
        self._zoom_at(event.x, event.y, 1.15 if steps > 0 else 1 / 1.15)

    def _pan_start(self, event):
        self._pan_anchor = (event.x, event.y)

    def _pan_move(self, event):
        if self._pan_anchor is None:
            return

        old_x, old_y = self._pan_anchor
        self.state.offset_x += event.x - old_x
        self.state.offset_y += event.y - old_y
        self._pan_anchor = (event.x, event.y)
        self.redraw()
