import pytest
from pathlib import Path
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.errors import UnsupportedFeatureError

def test_g01_route_still_unsupported(tmp_path:Path):
    p=tmp_path/"route.drl";p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG01X1Y1\nM30\n")
    with pytest.raises(UnsupportedFeatureError):ExcellonParser().parse(p)
