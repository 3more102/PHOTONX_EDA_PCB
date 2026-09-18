from dataclasses import dataclass
@dataclass(frozen=True)
class SearchPreset:
    name:str
    query:str
    scope:str="all"
    sort_field:str=""
    reverse:bool=False
