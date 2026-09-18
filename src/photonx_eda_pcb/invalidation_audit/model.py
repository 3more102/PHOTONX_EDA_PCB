from dataclasses import dataclass
@dataclass(frozen=True)
class InvalidationExpectation:
    changed:tuple[str,...]
    expected_recompute:tuple[str,...]
@dataclass(frozen=True)
class InvalidationResult:
    passed:bool
    planned:tuple[str,...]
    missing:tuple[str,...]
    unexpected:tuple[str,...]
