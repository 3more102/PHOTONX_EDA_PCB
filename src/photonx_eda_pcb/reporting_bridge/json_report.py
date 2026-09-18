import json
def unified_json(report):return json.dumps({"title":report.title,"sections":[{"name":s.name,"payload":s.payload} for s in report.sections]},sort_keys=True,separators=(",",":"),default=str)
