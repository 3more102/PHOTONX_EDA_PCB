from dataclasses import dataclass,field
@dataclass(frozen=True)
class VariantComponent:
    reference:str
    fitted:bool=True
    value:str|None=None
    footprint:str|None=None
@dataclass
class VariantDefinition:
    name:str
    components:dict[str,VariantComponent]=field(default_factory=dict)
    metadata:dict[str,object]=field(default_factory=dict)
