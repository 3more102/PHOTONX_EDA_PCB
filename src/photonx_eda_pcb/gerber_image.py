from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeVar, Generic

Polarity = Literal["dark", "clear"]
T = TypeVar("T")


@dataclass(frozen=True)
class ImageOperation(Generic[T]):
    """One ordered Gerber image operation.

    The operation stream is deliberately separate from the reconstructed board
    model.  LPC cannot be represented by simply tagging a Track/Pad/Region:
    Gerber polarity is an ordered image-composition operation, so clear objects
    must subtract from the image accumulated before them.
    """

    sequence: int
    polarity: Polarity
    geometry: T


class ImageCompositionStream(Generic[T]):
    """Deterministic ordered dark/clear operation stream.

    This is the semantic foundation for exact LPC support.  Consumers must
    compose operations in sequence order; they must not group by polarity.
    """

    def __init__(self) -> None:
        self._operations: list[ImageOperation[T]] = []
        self._next_sequence = 0

    def append(self, polarity: Polarity, geometry: T) -> ImageOperation[T]:
        if polarity not in {"dark", "clear"}:
            raise ValueError(f"invalid Gerber image polarity: {polarity!r}")
        op = ImageOperation(self._next_sequence, polarity, geometry)
        self._operations.append(op)
        self._next_sequence += 1
        return op

    @property
    def operations(self) -> tuple[ImageOperation[T], ...]:
        return tuple(self._operations)

    def clear(self) -> None:
        self._operations.clear()
        self._next_sequence = 0
