from .writer import write_schematic
import hashlib
def schematic_sha256(schematic):
    return hashlib.sha256(write_schematic(schematic).encode("utf-8")).hexdigest()
