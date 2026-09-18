import json
from .model import RuleProfile
def dumps_profile(p):return json.dumps({"name":p.name,"min_track_mm":p.min_track_mm,"min_clearance_mm":p.min_clearance_mm,"min_drill_mm":p.min_drill_mm,"min_annular_mm":p.min_annular_mm,"min_mask_sliver_mm":p.min_mask_sliver_mm,"net_overrides":p.net_overrides},sort_keys=True,separators=(",",":"))
def loads_profile(text):
    d=json.loads(text);return RuleProfile(str(d["name"]),float(d["min_track_mm"]),float(d["min_clearance_mm"]),float(d["min_drill_mm"]),float(d["min_annular_mm"]),float(d["min_mask_sliver_mm"]),dict(d.get("net_overrides",{})))
