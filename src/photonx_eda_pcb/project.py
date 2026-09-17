from __future__ import annotations
from pathlib import Path
from .config import ReconstructionConfig
from .pipeline import reconstruct


def load_project(input_dir: str | Path, config: ReconstructionConfig | None = None):
    """Compatibility helper returning only the board model."""
    return reconstruct(input_dir, config).board
