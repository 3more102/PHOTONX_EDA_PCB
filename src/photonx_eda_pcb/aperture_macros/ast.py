from dataclasses import dataclass,field
@dataclass(frozen=True)
class MacroPrimitive:
    code:int
    modifiers:tuple[str,...]
@dataclass
class MacroDefinition:
    name:str
    primitives:list[MacroPrimitive]=field(default_factory=list)
