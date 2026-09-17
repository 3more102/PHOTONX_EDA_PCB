from photonx_eda_pcb.workspace import WorkspaceState
from photonx_eda_pcb.workspace.dirty import mark_dirty,mark_clean
from photonx_eda_pcb.workspace.locks import WorkspaceLock
def test_workspace_state_and_lock():
    state=WorkspaceState("demo","input"); mark_dirty(state); assert state.dirty; mark_clean(state); assert not state.dirty
    lock=WorkspaceLock(); assert lock.acquire("a") and not lock.acquire("b") and lock.release("a")
