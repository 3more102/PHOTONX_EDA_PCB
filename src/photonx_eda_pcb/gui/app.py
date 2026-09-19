from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from .canvas import BoardCanvas
from .inspector import Inspector
from .state import ViewState


_ALL_NETS = "<All nets>"


def launch(input_dir: str | Path) -> None:
    result = reconstruct(input_dir)

    root = tk.Tk()
    root.title("PHOTONX EDA PCB — Evidence Viewer")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    state = ViewState(result.board)

    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    inspector = Inspector(frame, state)
    inspector.grid(row=0, column=1, sticky="ns")

    net_ids = [net.id for net in result.board.nets]
    nets = ttk.Combobox(
        frame,
        values=[_ALL_NETS, *net_ids],
        state="readonly",
    )
    nets.set(_ALL_NETS)
    nets.grid(row=1, column=0, sticky="ew")

    def show_selection(object_id: str | None):
        inspector.show(object_id)
        nets.set(state.highlighted_net_id or _ALL_NETS)

    canvas = BoardCanvas(
        frame,
        state,
        on_select=show_selection,
    )
    canvas.grid(row=0, column=0, sticky="nsew")

    def highlight(_event=None):
        value = nets.get()
        state.highlight_net(None if value == _ALL_NETS else value)
        canvas.redraw()

    def clear_selection(_event=None):
        state.select(None, sync_net=True)
        nets.set(_ALL_NETS)
        inspector.show(None)
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)
    root.bind("<Escape>", clear_selection)

    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'} | "
        f"errors={len(result.validation.errors)} | "
        f"warnings={len(result.validation.warnings)} | "
        "wheel=zoom | middle-drag=pan | Esc=clear"
    )
    ttk.Label(frame, text=status).grid(
        row=1,
        column=1,
        sticky="ew",
    )

    root.geometry("1180x740")
    root.mainloop()
