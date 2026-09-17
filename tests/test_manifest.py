from pathlib import Path
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files
FIX=Path(__file__).parent/"fixtures"/"led"

def test_manifest_classifies_inputs():
    files=discover_manufacturing_files(FIX); assert [f.kind for f in files].count("drill")==1; assert [f.kind for f in files].count("gerber")==2; assert any(f.layer=="Edge.Cuts" for f in files)
