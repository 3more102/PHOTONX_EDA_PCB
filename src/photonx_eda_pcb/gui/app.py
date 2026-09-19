from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from .canvas import BoardCanvas
from .confidence import net_confidence_summary
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

    ttk.Label(controls, text="Net").grid(row=0, column=0, padx=(0, 6))
    nets = ttk.Combobox(
        controls,
        values=[net.id for net in result.board.nets],
        state="readonly",
    )
    nets.grid(row=0, column=1, sticky="ew")

    def highlight(_event=None):
        state.highlighted_net_id = nets.get() or None
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)

    heatmap_var = tk.BooleanVar(value=state.show_confidence_heatmap)

    def toggle_heatmap():
        state.show_confidence_heatmap = bool(heatmap_var.get())
        canvas.redraw()

    ttk.Checkbutton(
        controls,
        text="Confidence heatmap",
        variable=heatmap_var,
        command=toggle_heatmap,
    ).grid(row=0, column=2, padx=(10, 0))

    confidence = net_confidence_summary(result.board)
    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'}"
        f" | errors={len(result.validation.errors)}"
        f" | warnings={len(result.validation.warnings)}"
        f" | net confidence H/M/L/U="
        f"{confidence['high']}/{confidence['medium']}/{confidence['low']}/{confidence['unknown']}"
    )
    ttk.Label(frame, text=status).grid(row=1, column=1, sticky="ew")

    root.geometry("1100x700")
    root.mainloop()
