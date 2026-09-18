from dataclasses import dataclass
@dataclass(frozen=True)
class MemorySample:
    name:str
    current_bytes:int
    peak_bytes:int
    result_size:int|None=None
