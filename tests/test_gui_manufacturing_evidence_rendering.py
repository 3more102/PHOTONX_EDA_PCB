import tkinter as tk

from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.gui.canvas import BoardCanvas
from photonx_eda_pcb.gui.state import ViewState
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    DrillHit,
    PadCandidate,
    Point,
    Track,
)


class RecordingCanvas:
    xy = BoardCanvas.xy
    redraw = BoardCanvas.redraw

    def __init__(self, state):
        self.state = state
        self.calls = []

    def delete(self, *args):
        self.calls.append(("delete", args, {}))

    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))
        return len(self.calls)

    def create_oval(self, *args, **kwargs):
        self.calls.append(("oval", args, kwargs))
        return len(self.calls)

    def create_polygon(self, *args, **kwargs):
        self.calls.append(("polygon", args, kwargs))
        return len(self.calls)

    def find_withtag(self, _tag):
        return ()

    def itemconfigure(self, *_args, **_kwargs):
        raise AssertionError("no selected object expected")


def test_canvas_renders_all_physical_board_evidence_without_tk_root():
    region = CopperRegion(
        "REGION",
        (
            Point(0, 0),
            Point(4, 0),
            Point(4, 4),
            Point(0, 4),
        ),
        "F.Cu",
        net_id="N1",
        holes=(
            (
                Point(1, 1),
                Point(2, 1),
                Point(2, 2),
                Point(1, 2),
            ),
        ),
    )
    board = BoardModel(
        tracks=[Track("TRACK", Point(0, 5), Point(2, 5), 0.2, "F.Cu", "N1")],
        pads=[PadCandidate("PAD", Point(3, 5), 1, 1, "C", "F.Cu", net_id="N1")],
        drills=[DrillHit("DRILL", Point(3, 5), 0.4, "plated")],
        slots=[SlotFeature("SLOT", (5, 0), (7, 0), 0.8, "unknown")],
        routes=[RoutedPath("ROUTE", ((5, 2), (6, 2), (6, 3)), 0.5, "unknown")],
        regions=[region],
    )
    state = ViewState(board)
    state.highlighted_net_id = "OTHER"
    canvas = RecordingCanvas(state)

    canvas.redraw()

    tagged = [
        (kind, kwargs.get("tags"), kwargs)
        for kind, _args, kwargs in canvas.calls
        if "tags" in kwargs
    ]

    assert any(kind == "polygon" and tags == ("REGION", "region") for kind, tags, _ in tagged)
    assert any(kind == "polygon" and tags == ("REGION", "region-hole") for kind, tags, _ in tagged)
    assert any(kind == "line" and tags == ("TRACK", "track") and kwargs.get("dash") == (2, 3) for kind, tags, kwargs in tagged)
    assert any(kind == "oval" and tags == ("PAD", "pad") and kwargs.get("stipple") == "gray50" for kind, tags, kwargs in tagged)
    assert any(kind == "oval" and tags == ("DRILL", "drill") for kind, tags, _ in tagged)
    assert any(kind == "line" and tags == ("SLOT", "slot") for kind, tags, _ in tagged)
    assert any(kind == "line" and tags == ("ROUTE", "route") for kind, tags, _ in tagged)


def test_canvas_uses_round_caps_for_routed_and_slotted_evidence():
    board = BoardModel(
        slots=[SlotFeature("SLOT", (0, 0), (1, 0), 0.5, "unknown")],
        routes=[RoutedPath("ROUTE", ((0, 1), (1, 1)), 0.25, "unknown")],
    )
    canvas = RecordingCanvas(ViewState(board))

    canvas.redraw()

    physical_lines = [
        kwargs
        for kind, _args, kwargs in canvas.calls
        if kind == "line" and kwargs.get("tags", (None,))[0] in {"SLOT", "ROUTE"}
    ]
    assert len(physical_lines) == 2
    assert all(call["capstyle"] == tk.ROUND for call in physical_lines)
