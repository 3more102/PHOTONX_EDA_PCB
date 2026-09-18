from pathlib import Path
from photonx_eda_pcb.pipeline import reconstruct
from photonx_eda_pcb.config import ReconstructionConfig

def test_reconstruct_propagates_slots(tmp_path:Path):
    (tmp_path/"board.drl").write_text("M48\nMETRIC\nT01C0.800\n%\nT01\nX1.000Y1.000G85X3.000Y1.000\nM30\n")
    r=reconstruct(tmp_path,ReconstructionConfig(strict_parsing=True))
    assert len(r.board.slots)==1
    assert r.board.slots[0].width_mm==.8
