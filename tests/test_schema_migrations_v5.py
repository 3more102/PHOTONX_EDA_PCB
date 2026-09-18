from photonx_eda_pcb.schema_migrations.defaults import default_registry
from photonx_eda_pcb.schema_migrations.runner import migrate_payload
def test_project_v1_to_v2():
    p={"name":"x","schema_version":1,"artifacts":[{"role":"gerber_copper","path":"a.gbr"}]}
    q=migrate_payload(p,2,default_registry())
    assert q["schema_version"]==2 and q["artifacts"][0]["sha256"]=="" and "metadata" in q
