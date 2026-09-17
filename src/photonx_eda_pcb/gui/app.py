from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from ..pipeline import reconstruct
from .state import ViewState
from .canvas import BoardCanvas
from .inspector import Inspector


def launch(input_dir: str | Path) -> None:
    result = reconstruct(input_dir); root = tk.Tk(); root.title("PHOTONX EDA PCB — Evidence Viewer"); state = ViewState(result.board)
    root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1); frame=ttk.Frame(root); frame.grid(row=0,column=0,sticky="nsew"); frame.columnconfigure(0,weight=1); frame.rowconfigure(0,weight=1)
    inspector=Inspector(frame,state); inspector.grid(row=0,column=1,sticky="ns"); canvas=BoardCanvas(frame,state,on_select=inspector.show); canvas.grid(row=0,column=0,sticky="nsew")
    nets=ttk.Combobox(frame,values=[n.id for n in result.board.nets],state="readonly"); nets.grid(row=1,column=0,sticky="ew")
    def highlight(_event=None): state.highlighted_net_id=nets.get() or None; canvas.redraw()
    nets.bind("<<ComboboxSelected>>",highlight); status=f"validation={'PASS' if result.validation.ok else 'FAIL'} | errors={len(result.validation.errors)} | warnings={len(result.validation.warnings)}"; ttk.Label(frame,text=status).grid(row=1,column=1,sticky="ew"); root.geometry("1100x700"); root.mainloop()
