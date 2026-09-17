from dataclasses import dataclass, field
@dataclass
class Outcome:
    value:object|None=None
    warnings:list[str]=field(default_factory=list)
    errors:list[str]=field(default_factory=list)
    @property
    def ok(self)->bool: return not self.errors
