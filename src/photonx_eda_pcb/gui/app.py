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
    root.geometry("1100x700")
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
    controls.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
    controls.columnconfigure(1, weight=1)

    ttk.Label(controls, text="Physical net:").grid(row=0, column=0, padx=(0, 6))
    net_values = ["All nets", *[net.id for net in result.board.nets]]
    nets = ttk.Combobox(controls, values=net_values, state="readonly")
    nets.grid(row=0, column=1, sticky="ew")
    nets.current(0)

    def highlight(_event=None):
        value = nets.get()
        state.highlighted_net_id = None if value == "All nets" else value
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)
    ttk.Button(controls, text="Fit", command=canvas.fit_to_board).grid(
        row=0, column=2, padx=(8, 0)
    )
    ttk.Label(
        controls,
        text="Wheel: zoom at cursor · Middle-drag: pan",
    ).grid(row=0, column=3, padx=(10, 0))

    board = result.board
    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'}"
        f" | errors={len(result.validation.errors)}"
        f" | warnings={len(result.validation.warnings)}"
        f"\ntracks={len(board.tracks)} pads={len(board.pads)}"
        f" regions={len(board.regions)} drills={len(board.drills)}"
        f" slots={len(board.slots)} routes={len(board.routes)}"
        f" nets={len(board.nets)}"
    )
    ttk.Label(
        frame,
        text=status,
        justify="left",
        wraplength=330,
    ).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

    root.after_idle(canvas.fit_to_board)
    root.mainloop()
