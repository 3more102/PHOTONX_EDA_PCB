from dataclasses import dataclass
@dataclass(frozen=True)
class FormatGuess:
    format:str
    confidence:float
    reasons:tuple[str,...]=()
