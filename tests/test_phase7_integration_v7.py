from photonx_eda_pcb.pipeline_dag import DagNode,PipelineDag,execute_dag
from photonx_eda_pcb.snapshot_store import SnapshotStore
from photonx_eda_pcb.event_log import EventLog
from photonx_eda_pcb.artifact_bundle import build_bundle
from photonx_eda_pcb.diagnostic_catalog import default_catalog
def test_phase7_flow():
    log=EventLog()
    d=PipelineDag().add(DagNode("parse",lambda i:{"parsed":"ok"},(),("parsed",))).add(DagNode("export",lambda i:{"report":"done"},("parsed",),("report",)))
    r=execute_dag(d);log.append("pipeline","complete",data={"executed":r.executed})
    s=SnapshotStore();snap=s.create(str(r.artifacts),"pipeline")
    b=build_bundle("release",[{"path":"report.txt","role":"report","content":r.artifacts["report"]}])
    assert snap.sha256 and len(b.entries)==1 and len(log)==1 and default_catalog().get("LOW_CONFIDENCE")
