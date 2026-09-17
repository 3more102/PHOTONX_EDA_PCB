from pathlib import Path
from ..io.manifest import build_manifest
from ..io.json_codec import dump_json
def export_source_manifest(source_dir:str|Path,path:str|Path)->Path: return dump_json(build_manifest(source_dir),path)
