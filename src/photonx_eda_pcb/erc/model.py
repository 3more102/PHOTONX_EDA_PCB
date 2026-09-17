from dataclasses import dataclass
@dataclass(frozen=True)
class ErcIssue: severity:str; code:str; message:str; ref:str|None=None
