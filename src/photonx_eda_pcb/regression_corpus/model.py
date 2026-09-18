from dataclasses import dataclass,field
@dataclass(frozen=True)
class CorpusExpectation:
    metrics:dict[str,object]
    tolerances:dict[str,float]=field(default_factory=dict)
    unknowns:tuple[str,...]=()
@dataclass(frozen=True)
class CorpusCase:
    id:str
    category:str
    inputs:tuple[str,...]
    expectation:CorpusExpectation
    synthetic:bool=True
    description:str=""
    tags:tuple[str,...]=()
@dataclass
class Corpus:
    cases:list[CorpusCase]=field(default_factory=list)
