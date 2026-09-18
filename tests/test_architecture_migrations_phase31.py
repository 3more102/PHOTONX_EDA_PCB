from photonx_eda_pcb.architecture_migrations.defaults import default_migrations
from photonx_eda_pcb.architecture_migrations import MigrationRegistry,validate_migration_plan
def test_default_architecture_migrations_are_valid():
    plans=default_migrations();r=MigrationRegistry()
    for p in plans:r.add(p)
    assert len(r.all())==2 and all(validate_migration_plan(p)==[] for p in plans)
    assert r.get("MIG-VALIDATION").status=="active"
