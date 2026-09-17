from pathlib import Path
from photonx_eda_pcb import reconstruct
FIX=Path(__file__).parent/"fixtures"/"led"

def test_end_to_end_reconstruction():
    result=reconstruct(FIX); b=result.board; assert result.validation.ok; assert len(b.pads)==6; assert len(b.tracks)==4; assert len(b.drills)==6; assert len(b.outline)==4; assert len(b.nets)==3; assert sorted(len(n.members) for n in b.nets)==[3,3,4]; assert all(p.drill==0.8 for p in b.pads)

def test_reconstruction_ids_are_stable():
    first=reconstruct(FIX).board; second=reconstruct(FIX).board; assert [p.id for p in first.pads]==[p.id for p in second.pads]; assert [n.id for n in first.nets]==[n.id for n in second.nets]
