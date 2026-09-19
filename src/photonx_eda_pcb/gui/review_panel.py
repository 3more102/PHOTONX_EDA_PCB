from __future__ import annotations

from tkinter import ttk

from .review import collect_review_items
from .state import ViewState


class ReviewPanel(ttk.Frame):
    def __init__(self, master, state: ViewState, validation, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state
        self.validation = validation
        self.on_select = on_select
        self._object_by_item: dict[str, str | None] = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            self,
            columns=("severity", "category", "code", "message"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("severity", text="Severity")
        self.tree.heading("category", text="Category")
        self.tree.heading("code", text="Code")
        self.tree.heading("message", text="Message")
        self.tree.column("severity", width=75, stretch=False)
        self.tree.column("category", width=90, stretch=False)
        self.tree.column("code", width=180, stretch=False)
        self.tree.column("message", width=360, stretch=True)

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._select)
        self.refresh()

    def refresh(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self._object_by_item.clear()

        for item in collect_review_items(self.state.board, self.validation):
            row_id = self.tree.insert(
                "",
                "end",
                values=(item.severity, item.category, item.code, item.message),
            )
            self._object_by_item[row_id] = item.object_id

    def _select(self, _event=None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        object_id = self._object_by_item.get(selection[0])
        if object_id is None:
            return
        self.state.selected_id = object_id
        if self.on_select is not None:
            self.on_select(object_id)
