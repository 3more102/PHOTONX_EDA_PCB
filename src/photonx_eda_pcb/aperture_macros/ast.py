from dataclasses import dataclass,field

@dataclass(frozen=True)
class MacroPrimitive:
    code:int
    modifiers:tuple[str,...]

@dataclass(frozen=True)
class MacroVariableDefinition:
    index:int
    expression:str

@dataclass
class MacroDefinition:
    name:str
    primitives:list[MacroPrimitive | MacroVariableDefinition]=field(default_factory=list)
