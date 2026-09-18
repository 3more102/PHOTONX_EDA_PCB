from photonx_eda_pcb.project_file_format import ProjectFile,ProjectArtifact,dumps_project,loads_project,validate_project_file
def test_project_file_roundtrip():
    p=ProjectFile("demo",2,[ProjectArtifact("gerber_copper","fab/top.gbr","a"*64,True)],{"units":"mm"},{"owner":"test"})
    q=loads_project(dumps_project(p))
    assert q.name=="demo" and q.schema_version==2 and q.artifacts[0].path=="fab/top.gbr"
    assert validate_project_file(q)==[]
