from photonx_eda_pcb.project_file_format import ProjectFile,ProjectArtifact,dumps_project
from photonx_eda_pcb.schema_migrations.defaults import default_registry
from photonx_eda_pcb.schema_migrations.runner import migrate_payload
from photonx_eda_pcb.plugin_api import PluginMetadata,PluginRegistry
from photonx_eda_pcb.batch_cli import BatchJob,run_batch
from photonx_eda_pcb.batch_cli.registry import BatchCommandRegistry
def test_phase5_platform_flow():
    p=ProjectFile("P",2,[ProjectArtifact("gerber_copper","top.gbr")])
    assert '"name":"P"' in dumps_project(p)
    assert migrate_payload({"name":"P","schema_version":1,"artifacts":[]},2,default_registry())["schema_version"]==2
    class Plug: metadata=PluginMetadata("x","1",1,("parser",))
    reg=PluginRegistry();reg.register(Plug());assert reg.names()==["x"]
    br=BatchCommandRegistry();br.register("count",lambda job,ctx:len(job.inputs))
    assert run_batch([BatchJob("1","count",("a","b"))],br)[0].output==2
