from photonx_eda_pcb.schema_migrations.defaults import default_registry
from photonx_eda_pcb.schema_migrations.validation import validate_migration_path
def test_default_path_valid():
    assert validate_migration_path(1,2,default_registry())==[]
