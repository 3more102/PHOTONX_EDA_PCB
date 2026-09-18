from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .config import ReconstructionConfig
from .models import BoardModel, ParseDiagnostic
from .parsers import discover_manufacturing_files, GerberRS274XParser, ExcellonParser
from .connectivity import attach_drills, build_physical_graph, assign_physical_nets
from .inference import infer_component_hypotheses
from .validation import ValidationReport, validate_board

@dataclass
class ReconstructionResult:
    board: BoardModel
    validation: ValidationReport

def reconstruct(directory:str|Path,config:ReconstructionConfig|None=None)->ReconstructionResult:
    cfg=config or ReconstructionConfig();board=BoardModel(metadata={"source_directory":str(Path(directory))})
    files=discover_manufacturing_files(directory)
    if not files:raise FileNotFoundError(f"no manufacturing files found in {directory}")
    for item in files:
        if item.kind=="drill":
            r=ExcellonParser(strict=cfg.strict_parsing).parse(item.path)
            board.drills.extend(r.drills);board.slots.extend(r.slots);board.diagnostics.extend(r.diagnostics);continue
        layer=item.layer
        if layer is None:
            board.diagnostics.append(ParseDiagnostic("warning","UNKNOWN_LAYER","Gerber file skipped because layer could not be inferred",str(item.path)));continue
        r=GerberRS274XParser(layer,strict=cfg.strict_parsing).parse(item.path)
        board.tracks.extend(r.tracks);board.pads.extend(r.pads);board.outline.extend(r.outline);board.diagnostics.extend(r.diagnostics)
    attach_drills(board,cfg.drill_attach_tolerance_mm)
    graph=build_physical_graph(board,cfg.connectivity_tolerance_mm)
    assign_physical_nets(board,graph)
    infer_component_hypotheses(board,cfg.component_pair_distance_mm)
    return ReconstructionResult(board,validate_board(board))
