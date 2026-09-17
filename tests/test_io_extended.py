from photonx_eda_pcb.io.inventory import inventory
from photonx_eda_pcb.io.checksums import checksum_manifest
from photonx_eda_pcb.io.discover import discover_manufacturing_files
from photonx_eda_pcb.io.manifest import build_manifest
from photonx_eda_pcb.io.safe_write import atomic_write_text
def test_inventory_manifest_and_discovery(tmp_path):
 (tmp_path/"a.gbr").write_text("G04 test*"); (tmp_path/"b.drl").write_text("M48"); (tmp_path/"n.txt").write_text("x")
 assert len(inventory(tmp_path))==3 and len(checksum_manifest(tmp_path))==3
 d=discover_manufacturing_files(tmp_path); assert len(d["gerber"])==1 and len(d["drill"])==1
 m=build_manifest(tmp_path); assert len(m["sha256"])==3
 p=atomic_write_text(tmp_path/"out.txt","ok"); assert p.read_text()=="ok"
