from dataclasses import dataclass,field
@dataclass(frozen=True)
class BatchJob:
    id:str
    command:str
    inputs:tuple[str,...]=()
    options:dict=field(default_factory=dict)
@dataclass
class BatchResult:
    job_id:str
    success:bool
    output:object=None
    error:str=""
