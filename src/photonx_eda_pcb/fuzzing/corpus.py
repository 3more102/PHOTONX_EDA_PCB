from dataclasses import dataclass

@dataclass(frozen=True)
class CorpusCase:
    name:str
    payload:str
    expected_exception:str|None=None
