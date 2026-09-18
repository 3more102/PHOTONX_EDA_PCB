from dataclasses import dataclass,field
@dataclass(frozen=True)
class ConformanceExpectation:
    counts:dict[str,int]=field(default_factory=dict)
    diagnostic_codes:tuple[str,...]=()
    exception_type:str|None=None
@dataclass(frozen=True)
class ConformanceCase:
    id:str
    format:str
    text:str
    expectation:ConformanceExpectation
    strict:bool=True
    layer:str="F.Cu"
    description:str=""
@dataclass(frozen=True)
class ConformanceResult:
    id:str
    passed:bool
    counts:dict[str,int]
    diagnostics:tuple[str,...]
    exception_type:str|None
    differences:tuple[str,...]=()
