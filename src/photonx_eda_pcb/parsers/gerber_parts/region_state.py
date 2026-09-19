from dataclasses import dataclass, field


@dataclass
class RegionState:
    active: bool = False
    vertices: list[tuple[float, float]] = field(default_factory=list)

    def begin(self) -> None:
        self.active = True
        self.vertices.clear()

    def add(self, x: float, y: float) -> None:
        if not self.active:
            raise RuntimeError("region not active")
        self.vertices.append((x, y))

    def end(self) -> tuple[tuple[float, float], ...]:
        if not self.active:
            raise RuntimeError("region not active")
        self.active = False
        return tuple(self.vertices)

    def abort(self) -> None:
        self.active = False
        self.vertices.clear()
