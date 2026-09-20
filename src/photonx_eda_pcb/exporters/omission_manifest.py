import json
from pathlib import Path

def omission_manifest(report):
    return {
      "exported_slots":list(getattr(report,"exported_slot_ids",())),
      "exported_pads":list(getattr(report,"exported_pad_ids",())),
      "skipped_pads":list(getattr(report,"skipped_pad_ids",())),
      "skipped_slots":list(getattr(report,"skipped_slot_ids",())),
      "exported_regions":list(getattr(report,"exported_region_ids",())),
      "skipped_regions":list(getattr(report,"skipped_region_ids",())),
      "exported_tracks":list(getattr(report,"exported_track_ids",())),
      "skipped_tracks":list(getattr(report,"skipped_track_ids",())),
      "omitted_routes":list(getattr(report,"skipped_route_ids",())),
      "omitted_via_spans":list(getattr(report,"skipped_via_span_ids",())),
      "issues":[{"severity":x.severity,"code":x.code,"object_id":x.object_id,"message":x.message} for x in report.issues]
    }

def write_omission_manifest(report,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(omission_manifest(report),indent=2,sort_keys=True),encoding="utf-8")
    return p
