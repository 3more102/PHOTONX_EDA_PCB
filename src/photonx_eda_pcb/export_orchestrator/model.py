from dataclasses import dataclass,field
@dataclass(frozen=True)
class ExportRequest:
    id:str
    format:str
    options:dict=field(default_factory=dict)
@dataclass
class ExportResult:
    request_id:str
    success:bool
    content:object=None
    error:str=""
