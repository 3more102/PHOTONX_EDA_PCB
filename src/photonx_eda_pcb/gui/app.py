from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..pipeline import reconstruct
from ..review_queue import ReviewItem, build_board_review_queue
from .canvas import BoardCanvas
from .inspector import Inspector
from .state import ViewState
from .via_review import build_via_evidence_rows


def _review_confidence_text(item) -> str:
    if not item.metadata.get("confidence_available", True):
        return "—"
    return f"{item.confidence:.3f}"


def _confidence_text(value) -> str:
    return "—" if value is None else f"{float(value):.3f}"


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

    tabs = ttk.Notebook(side)
    tabs.grid(row=1, column=0, sticky="nsew")

    review_tab = ttk.Frame(tabs)
    review_tab.rowconfigure(0, weight=1)
    review_tab.columnconfigure(0, weight=1)
    tabs.add(review_tab, text="Evidence Review")

    review_queue = build_board_review_queue(
        result.board,
        validation=result.validation,
    )
    review = ttk.Treeview(
        review_tab,
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
    review.grid(row=0, column=0, sticky="nsew")

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
        elif item.kind in {"diagnostic", "validation", "via_span"}:
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

    via_tab = ttk.Frame(tabs)
    via_tab.rowconfigure(0, weight=1)
    via_tab.columnconfigure(0, weight=1)
    tabs.add(via_tab, text="Via Evidence")

    via_rows = build_via_evidence_rows(result.board)
    via_rows_by_id = {row["id"]: row for row in via_rows}
    via = ttk.Treeview(
        via_tab,
        columns=(
            "status",
            "drill",
            "layers",
            "plating",
            "net",
            "confidence",
            "reason",
        ),
        show="headings",
        height=10,
    )
    via.heading("status", text="Status")
    via.heading("drill", text="Drill")
    via.heading("layers", text="Layer span")
    via.heading("plating", text="Plating")
    via.heading("net", text="Net")
    via.heading("confidence", text="Confidence")
    via.heading("reason", text="Evidence / omission reason")
    via.column("status", width=90, stretch=False)
    via.column("drill", width=130, stretch=False)
    via.column("layers", width=150, stretch=False)
    via.column("plating", width=85, stretch=False)
    via.column("net", width=110, stretch=False)
    via.column("confidence", width=90, stretch=False, anchor="center")
    via.column("reason", width=360, stretch=True)

    for row in via_rows:
        via.insert(
            "",
            "end",
            iid=row["id"],
            values=(
                row["status"],
                row["drill_id"],
                row["layers"],
                row["plating"],
                row["net"],
                _confidence_text(row["confidence"]),
                row["reason"],
            ),
        )
    via.grid(row=0, column=0, sticky="nsew")

    def inspect_via(_event=None):
        selection = via.selection()
        if not selection:
            return
        row = via_rows_by_id.get(selection[0])
        if row is None:
            return

        drill_id = row["drill_id"]
        if drill_id in result.board.object_index():
            state.selected_id = drill_id
        else:
            state.selected_id = None

        net_id = row.get("net_id")
        state.highlighted_net_id = net_id
        nets.set(net_id or "")

        inspector.show_review(
            ReviewItem(
                id=row["id"],
                kind="via_span",
                target_id=drill_id,
                reason=row["reason"],
                confidence=float(row["confidence"] or 0.0),
                metadata={
                    "confidence_available": row["confidence"] is not None,
                    "status": row["status"],
                    "plating": row["plating"],
                    "layer_span": row["layers"],
                    "net": row["net"],
                    "pad_ids": row["pad_ids"],
                    "export_code": row["export_code"],
                },
            )
        )
        canvas.redraw()

    via.bind("<<TreeviewSelect>>", inspect_via)

    status = (
        f"validation={'PASS' if result.validation.ok else 'FAIL'} | "
        f"errors={len(result.validation.errors)} | "
        f"warnings={len(result.validation.warnings)} | "
        f"review={len(review_queue.open_items())} | "
        f"via_evidence={len(via_rows)}"
    )
    ttk.Label(side, text=status).grid(row=2, column=0, sticky="ew")

    root.geometry("1480x800")
    root.mainloop()
