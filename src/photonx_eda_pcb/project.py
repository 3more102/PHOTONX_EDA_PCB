from __future__ import annotations
from pathlib import Path
from .models import BoardModel
from .gerber import GerberParser, parse_outline
from .excellon import parse_excellon
from .reconstruct import attach_drills, reconstruct_connectivity, infer_components


def load_project(input_dir: str | Path) -> BoardModel:
    d=Path(input_dir)
    tracks,pads=GerberParser('F.Cu').parse(d/'copper.gbr')
    board=BoardModel(tracks=tracks,pads=pads)
    if (d/'outline.gbr').exists(): board.outline=parse_outline(d/'outline.gbr')
    if (d/'drill.drl').exists(): board.holes=parse_excellon(d/'drill.drl')
    attach_drills(board)
    reconstruct_connectivity(board)
    infer_components(board)
    return board
