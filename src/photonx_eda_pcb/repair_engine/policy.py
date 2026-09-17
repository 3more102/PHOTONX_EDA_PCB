from dataclasses import dataclass,field
@dataclass
class RepairPolicy:
    allow_automatic:bool=False;allowed_kinds:set[str]=field(default_factory=lambda:{'remove_zero_area','clear_stale_net_link'})
    def permits(self,candidate):return self.allow_automatic and candidate.automatic and candidate.kind in self.allowed_kinds
