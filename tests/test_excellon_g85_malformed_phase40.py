import pytest
from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import UnsupportedFeatureError

def test_malformed_g85_strict_rejected(tmp_path:Path):
    p=tmp_path/"bad.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y2G85X3\nM30\n")
    with pytest.raises(UnsupportedFeatureError):ExcellonParser(strict=True).parse(p)

def test_malformed_g85_permissive_diagnostic(tmp_path:Path):
    p=tmp_path/"bad.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y2G85X3\nM30\n")
    r=ExcellonParser(strict=False).parse(p)
    assert [d.code for d in r.diagnostics]==["UNSUPPORTED_EXCELLON_SLOT"]
