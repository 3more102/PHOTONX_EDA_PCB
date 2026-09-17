import pytest
from photonx_eda_pcb.core.ids import StableIdFactory
from photonx_eda_pcb.core.units import mm_to_um,um_to_mm,mil_to_mm
from photonx_eda_pcb.core.collections import duplicates,unique_preserve_order
from photonx_eda_pcb.core.hashing import sha256_text,sha256_file
from photonx_eda_pcb.core.ranges import clamp
from photonx_eda_pcb.core.text import safe_label
def test_ids_are_stable(): assert StableIdFactory("P").reserve(3)==["P0","P1","P2"]
def test_units(): assert mm_to_um(1.234)==1234 and um_to_mm(2500)==2.5 and mil_to_mm(100)==pytest.approx(2.54)
def test_collections(): assert duplicates(["a","b","a"])==["a"] and unique_preserve_order([2,1,2])==[2,1]
def test_hash_file(tmp_path):
 p=tmp_path/"x"; p.write_text("abc"); assert sha256_file(p)==sha256_text("abc")
def test_small_helpers(): assert clamp(8,0,5)==5 and safe_label(" A / B ")=="A_B"
