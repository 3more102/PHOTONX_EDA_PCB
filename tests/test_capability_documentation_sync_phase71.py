from pathlib import Path

from photonx_eda_pcb.capabilities import CAPABILITIES


def _capabilities():
    return {item.name: item for item in CAPABILITIES}


def test_excellon_capability_aliases_remain_consistent():
    caps = _capabilities()
    linear = caps["Excellon linear routing"]
    legacy = caps["Excellon slots/routes"]

    assert linear.status == "partial"
    assert legacy.status == "partial"
    assert "G00" in linear.note and "G01" in linear.note
    assert "G85" in legacy.note and "G00" in legacy.note
    assert "G02/G03" in linear.note and "unsupported" in linear.note.lower()
    assert "G02/G03" in legacy.note and "unsupported" in legacy.note.lower()


def test_limitations_document_matches_excellon_capability_boundary():
    text = Path("docs/LIMITATIONS.md").read_text(encoding="utf-8")

    assert "Excellon G85 straight canned slots" in text
    assert "G00 -> M15 -> G01... -> M16/M17" in text
    assert "Excellon routed arcs (\`G02/G03\`)" in text
    assert "- Excellon routed slots/routes;" not in text


def test_limitations_keeps_gerber_high_level_boundary_explicit():
    text = Path("docs/LIMITATIONS.md").read_text(encoding="utf-8")
    caps = _capabilities()

    assert caps["Gerber arcs/regions/macros"].status == "not_implemented"
    assert "Gerber arcs in the production high-level parser" in text
    assert "Gerber regions in the production high-level parser" in text
    assert "Gerber aperture macros" in text
