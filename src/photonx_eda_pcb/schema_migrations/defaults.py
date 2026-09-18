from .registry import MigrationRegistry
from .model import Migration
from .project_v1_v2 import project_v1_to_v2
def default_registry():
    r=MigrationRegistry();r.add(Migration(1,2,project_v1_to_v2,"project-v1-v2"));return r
