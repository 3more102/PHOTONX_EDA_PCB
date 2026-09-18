from dataclasses import dataclass
@dataclass(frozen=True)
class FingerprintFeatures:
    component_kinds:tuple[tuple[str,int],...]
    component_degrees:tuple[int,...]
    net_degrees:tuple[int,...]
    net_roles:tuple[str,...]=()
    pin_edge_count:int=0
@dataclass(frozen=True)
class SubgraphFingerprint:
    seed:str
    radius:int
    topology_hash:str
    semantic_hash:str
    features:FingerprintFeatures
    nodes:tuple[str,...]
    confidence:float=1.0
