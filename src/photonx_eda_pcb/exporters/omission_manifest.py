import json
from pathlib import Path
from ..io.safe_write import atomic_write_text
def omission_manifest(report):
    return {
      "exported_slots":list(report.exported_slot_ids),
      "skipped_slots":list(report.skipped_slot_ids),
      "issues":[{"severity":x.severity,"code":x.code,"object_id":x.object_id,"message":x.message} for x in report.issues]
    }
def write_omission_manifest(report,path):
    p=Path(path)
    return atomic_write_text(p,json.dumps(omission_manifest(report),indent=2,sort_keys=True))
