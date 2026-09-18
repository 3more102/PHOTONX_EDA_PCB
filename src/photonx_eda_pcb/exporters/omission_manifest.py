import json
from pathlib import Path
def omission_manifest(report):
    return {
      "exported_slots":list(report.exported_slot_ids),
      "skipped_slots":list(report.skipped_slot_ids),
      "issues":[{"severity":x.severity,"code":x.code,"object_id":x.object_id,"message":x.message} for x in report.issues]
    }
def write_omission_manifest(report,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(omission_manifest(report),indent=2,sort_keys=True),encoding="utf-8")
    return p
