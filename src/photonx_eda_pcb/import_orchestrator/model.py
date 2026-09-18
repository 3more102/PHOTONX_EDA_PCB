from dataclasses import dataclass
@dataclass(frozen=True)
class ImportRequest:
    path:str
    text:str
    expected_format:str|None=None
@dataclass
class ImportResult:
    path:str
    success:bool
    format:str="unknown"
    document:object=None
    diagnostics:list[str]=None
    def __post_init__(self):
        if self.diagnostics is None:self.diagnostics=[]
