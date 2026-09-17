from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from ..models import ParseDiagnostic


@dataclass
class ParseResult:
    path: Path
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)


class ParserBackend(Protocol):
    def parse(self, path: str | Path): ...
