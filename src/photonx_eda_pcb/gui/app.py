from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from .canvas import BoardCanvas
from .inspector import Inspector
from .review_panel import ReviewPanel
from .state import ViewState


def launch(input_dir: str | Path) -> None:
    result = reconstruct(input_dir)
    root = tk.Tk()
    root.title("PHOTONX EDA PCB — Evidence Viewer")
    state = ViewState(result.board)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=0)
    frame.rowconfigure(0, weight=1)

    side = ttk.Notebook(frame)
    inspector = Inspector(side, state)
    side.add(inspector, text="Inspector")

    def show_from_canvas(object_id: str | None) -> None:
        inspector.show(object_id)
        side.select(inspector)

    canvas = BoardCanvas(frame, state, on_select=show_from_canvas)
    canvas.grid(row=0, column=0, sticky="nsew")

    def show_from_review(object_id: str) -> None:
        inspector.show(object_id)
        side.select(inspector)
        canvas.redraw()

    review = ReviewPanel(
        side,
        state,
        result.validation,
        on_select=show_from_review,
    )
    side.add(review, text=f"Review ({len(review.tree.get_children())})")
    side.grid(row=0, column=1, sticky="nsew")

    nets = ttk.Combobox(
        frame,
        values=[n.id for n in result.board.nets],
        state="readonly",
    )
    nets.grid(row=1, column=0, sticky="ew")

    def highlight(_event=None):
        state.highlighted_net_id = nets.get() or None
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)

    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'}"
        f" | errors={len(result.validation.errors)}"
        f" | warnings={len(result.validation.warnings)}"
        f" | review={len(review.tree.get_children())}"
    )
    ttk.Label(frame, text=status).grid(row=1, column=1, sticky="ew")

    root.geometry("1250x760")
    root.mainloop()
