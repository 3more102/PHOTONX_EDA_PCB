from pathlib import Path
def test_coding_roadmap_has_mermaid():
    p=Path("docs/CODING_ROADMAP.md")
    text=p.read_text(encoding="utf-8")
    assert "flowchart TD" in text
    assert "Physical Connectivity" in text
    assert "Round-trip Verification" in text
