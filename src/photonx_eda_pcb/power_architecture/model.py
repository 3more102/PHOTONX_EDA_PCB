from dataclasses import dataclass,field
@dataclass(frozen=True)
class PowerRail:
    net_id:str
    voltage:float|None
    components:tuple[str,...]
    confidence:float
@dataclass(frozen=True)
class PowerStage:
    component_id:str
    kind:str
    input_rails:tuple[str,...]
    output_rails:tuple[str,...]
    enable_nets:tuple[str,...]=()
    feedback_nets:tuple[str,...]=()
    confidence:float=.5
@dataclass
class PowerArchitecture:
    rails:dict[str,PowerRail]=field(default_factory=dict)
    stages:list[PowerStage]=field(default_factory=list)
    dependencies:list=field(default_factory=list)
    sequences:list=field(default_factory=list)
    decoupling:list=field(default_factory=list)
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
