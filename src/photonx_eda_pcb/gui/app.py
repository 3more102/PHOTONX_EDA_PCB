from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from ..review_queue import build_board_review_queue
from .canvas import BoardCanvas
from .inspector import Inspector
from .state import ViewState


def _review_confidence_text(item) -> str:
    if not item.metadata.get("confidence_available", True):
        return "—"
    return f"{item.confidence:.3f}"


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

    side = ttk.Frame(frame)
    side.grid(row=0, column=1, rowspan=2, sticky="nsew")
    side.rowconfigure(0, weight=3)
    side.rowconfigure(1, weight=2)
    side.rowconfigure(2, weight=1)
    side.columnconfigure(0, weight=1)

    inspector = Inspector(side, state)
    inspector.grid(row=0, column=0, sticky="nsew")

    canvas = BoardCanvas(frame, state, on_select=inspector.show)
    canvas.grid(row=0, column=0, sticky="nsew")

    nets = ttk.Combobox(
        frame,
        values=[net.id for net in result.board.nets],
        state="readonly",
    )
    nets.grid(row=1, column=0, sticky="ew")

    def highlight(_event=None):
        state.highlighted_net_id = nets.get() or None
        canvas.redraw()

    nets.bind("<<ComboboxSelected>>", highlight)

    review_queue = build_board_review_queue(
        result.board,
        validation=result.validation,
    )
    review = ttk.Treeview(
        side,
        columns=("kind", "target", "confidence", "reason"),
        show="headings",
        height=10,
    )
    review.heading("kind", text="Kind")
    review.heading("target", text="Target")
    review.heading("confidence", text="Confidence")
    review.heading("reason", text="Review reason")
    review.column("kind", width=90, stretch=False)
    review.column("target", width=150, stretch=False)
    review.column("confidence", width=90, stretch=False, anchor="center")
    review.column("reason", width=330, stretch=True)

    for item in review_queue.open_items():
        review.insert(
            "",
            "end",
            iid=item.id,
            values=(
                item.kind,
                item.target_id,
                _review_confidence_text(item),
                item.reason,
            ),
        )
    review.grid(row=1, column=0, sticky="nsew")

    def inspect_review(_event=None):
        selection = review.selection()
        if not selection:
            return
        item = review_queue.get(selection[0])
        if item is None:
            return

        if item.kind == "net":
            state.highlighted_net_id = item.target_id
            nets.set(item.target_id)
            state.selected_id = None
            inspector.show(item.target_id)
        elif item.kind in {"diagnostic", "validation"}:
            selectable = item.metadata.get("selectable_object_id")
            if selectable in result.board.object_index():
                state.selected_id = selectable
            else:
                state.selected_id = None
            inspector.show_review(item)
        else:
            if item.target_id in result.board.object_index():
                state.selected_id = item.target_id
            else:
                state.selected_id = None
            inspector.show(item.target_id)
        canvas.redraw()

    review.bind("<<TreeviewSelect>>", inspect_review)

    layer_frame = ttk.LabelFrame(side, text="Visible layers")
    layer_frame.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)
    layer_frame.columnconfigure(0, weight=1)
    layer_frame.rowconfigure(0, weight=1)

    layers = state.available_layers
    layer_list = tk.Listbox(
        layer_frame,
        selectmode=tk.MULTIPLE,
        exportselection=False,
        height=min(8, max(1, len(layers))),
    )
    layer_list.grid(row=0, column=0, columnspan=2, sticky="nsew")

    for index, layer in enumerate(layers):
        layer_list.insert("end", layer)
        if state.is_layer_visible(layer):
            layer_list.selection_set(index)

    def apply_layer_selection(_event=None):
        selected = {layer_list.get(index) for index in layer_list.curselection()}
        state.set_visible_layers(selected)
        canvas.redraw()

    def show_all_layers():
        state.show_all_layers()
        layer_list.selection_set(0, "end")
        canvas.redraw()

    def hide_all_layers():
        state.hide_all_layers()
        layer_list.selection_clear(0, "end")
        canvas.redraw()

    layer_list.bind("<<ListboxSelect>>", apply_layer_selection)
    ttk.Button(
        layer_frame,
        text="All",
        command=show_all_layers,
    ).grid(row=1, column=0, sticky="ew")
    ttk.Button(
        layer_frame,
        text="None",
        command=hide_all_layers,
    ).grid(row=1, column=1, sticky="ew")

    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'} | "
        f"errors={len(result.validation.errors)} | "
        f"warnings={len(result.validation.warnings)} | "
        f"review={len(review_queue.open_items())}"
    )
    ttk.Label(side, text=status).grid(row=3, column=0, sticky="ew")

    root.geometry("1280x760")
    root.mainloop()
