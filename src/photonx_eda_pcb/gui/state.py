from __future__ import annotations
from dataclasses import dataclass
from ..models import BoardModel


@dataclass
class ViewState:
    board: BoardModel
    selected_id: str | None = None
    highlighted_net_id: str | None = None
    show_confidence_heatmap: bool = False
    scale: float = 12.0
    offset_x: float = 30.0
    offset_y: float = 30.0
