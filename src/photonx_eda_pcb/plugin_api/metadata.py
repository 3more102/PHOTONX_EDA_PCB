from dataclasses import dataclass
@dataclass(frozen=True)
class PluginMetadata:
    name:str
    version:str
    api_version:int=1
    capabilities:tuple[str,...]=()
    author:str=""
