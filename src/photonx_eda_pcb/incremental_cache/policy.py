from dataclasses import dataclass
@dataclass(frozen=True)
class CachePolicy:
    enabled:bool=True
    max_entries:int=10000
    version:str="1"
