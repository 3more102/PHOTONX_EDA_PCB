from dataclasses import dataclass
@dataclass(frozen=True)
class MigrationStep:
    id:str
    source_api:str
    target_api:str
    strategy:str
    breaking:bool=False
@dataclass(frozen=True)
class MigrationPlan:
    id:str
    title:str
    steps:tuple[MigrationStep,...]
    status:str="proposed"
