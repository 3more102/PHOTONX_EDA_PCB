from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from .canvas import BoardCanvas
from .inspector import Inspector
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
    frame.rowconfigure(0, weight=1)

    inspector = Inspector(frame, state)
    inspector.grid(row=0, column=1, sticky="ns")

    canvas = BoardCanvas(frame, state, on_select=inspector.show)
    canvas.grid(row=0, column=0, sticky="nsew")

    controls = ttk.Frame(frame)
    controls.grid(row=1, column=0, sticky="ew")
    controls.columnconfigure(1, weight=1)

    ttk.Label(controls, text="Net:").grid(row=0, column=0, padx=(0, 4))
    all_nets = "All nets"
    nets = ttk.Combobox(
        controls,
        values=[all_nets, *[net.id for net in result.board.nets]],
        state="readonly",
    )
    nets.grid(row=0, column=1, sticky="ew")
    nets.set(all_nets)

    def highlight(_event=None):
        selected = nets.get()
        state.highlighted_net_id = None if selected == all_nets else selected
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)
    ttk.Button(controls, text="Fit board", command=canvas.fit_to_board).grid(
        row=0,
        column=2,
        padx=(6, 0),
    )

    object_count = len(result.board.object_index())
    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'}"
        f" | errors={len(result.validation.errors)}"
        f" | warnings={len(result.validation.warnings)}"
        f" | objects={object_count}"
    )
    ttk.Label(frame, text=status).grid(row=1, column=1, sticky="ew")

    root.geometry("1100x700")
    root.update_idletasks()
    canvas.fit_to_board()
    root.mainloop()
