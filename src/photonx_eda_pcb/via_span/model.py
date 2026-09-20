from dataclasses import dataclass, field

@dataclass
class ViaSpanCandidate:
    drill_id: str
    from_layer: str | None
    to_layer: str | None
    confidence: float
    evidence: list[str] = field(default_factory=list)
    proven: bool = False
    pad_ids: tuple[str, ...] = ()
    layer_ids: tuple[str, ...] = ()

    def layers(self):
        if self.layer_ids:
            return self.layer_ids
        return tuple(x for x in (self.from_layer, self.to_layer) if x is not None)
