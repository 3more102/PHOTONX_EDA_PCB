from pathlib import Path
def test_phase2_roadmap_mermaid():
    t=Path("docs/CODING_ROADMAP_PHASE2.md").read_text(encoding="utf-8")
    assert "flowchart LR" in t
    assert "IPC-356" in t
    assert "KiCad Schematic" in t
