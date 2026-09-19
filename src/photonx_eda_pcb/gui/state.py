from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import BoardModel

EDGE_CUTS_LAYER = "Edge.Cuts"


def _layer_sort_key(layer: str) -> tuple[int, int | str]:
    if layer == "F.Cu":
        return (0, 0)
    match = re.fullmatch(r"In(\d+)\.Cu", layer)
    if match:
        return (1, int(match.group(1)))
    if layer == "B.Cu":
        return (2, 0)
    if layer == EDGE_CUTS_LAYER:
        return (3, 0)
    return (4, layer)


def board_layers(board: BoardModel) -> tuple[str, ...]:
    layers = {
        obj.layer
        for obj in (*board.tracks, *board.pads, *board.regions)
        if isinstance(obj.layer, str) and obj.layer
    }
    if board.outline:
        layers.add(EDGE_CUTS_LAYER)
    return tuple(sorted(layers, key=_layer_sort_key))


@dataclass
class ViewState:
    board: BoardModel
    selected_id: str | None = None
    highlighted_net_id: str | None = None
    scale: float = 12.0
    offset_x: float = 30.0
    offset_y: float = 30.0
    visible_layers: set[str] | None = None

    def __post_init__(self) -> None:
        if self.visible_layers is None:
            self.visible_layers = set(self.available_layers)
        else:
            self.set_visible_layers(self.visible_layers)

    @property
    def available_layers(self) -> tuple[str, ...]:
        return board_layers(self.board)

    def is_layer_visible(self, layer: str) -> bool:
        return layer in self.visible_layers

    def set_visible_layers(self, layers) -> None:
        available = set(self.available_layers)
        self.visible_layers = {str(layer) for layer in layers if str(layer) in available}

    def show_all_layers(self) -> None:
        self.visible_layers = set(self.available_layers)

    def hide_all_layers(self) -> None:
        self.visible_layers = set()
