from dataclasses import dataclass
@dataclass(frozen=True)
class ConnectorPath:
    connector_id:str
    target_id:str
    nodes:tuple[str,...]
    hops:int
    confidence:float
