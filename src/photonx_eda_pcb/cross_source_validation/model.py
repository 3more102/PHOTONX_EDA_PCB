from dataclasses import dataclass

@dataclass(frozen=True)
class SourceObservation:
    source:str
    subject_id:str
    field:str
    value:object
    confidence:float=1.0
