from photonx_eda_pcb.project_session import ProjectSession,dump_session,load_session,validate_session
from photonx_eda_pcb.project_session.documents import open_document,close_document
def test_session_roundtrip():
    s=ProjectSession("P");open_document(s,"a.kicad_pcb")
    t=load_session(dump_session(s))
    assert t.active_board=="a.kicad_pcb" and validate_session(t)==[]
    close_document(t,"a.kicad_pcb");assert t.active_board is None
