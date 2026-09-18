from photonx_eda_pcb.project_session import ProjectSession
from photonx_eda_pcb.project_session.dirty import mark_dirty,mark_saved
def test_dirty_revision():
    s=ProjectSession("P");mark_dirty(s)
    assert s.dirty and s.revision==1
    mark_saved(s);assert not s.dirty
