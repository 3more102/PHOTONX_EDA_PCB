import json
from .case import CorpusCase
def load_case_json(text):
    d=json.loads(text);return CorpusCase(d["id"],list(d.get("input_paths",[])),dict(d.get("expected_metrics",{})),dict(d.get("expected_nets",{})),d.get("notes",""))
def dump_case_json(case):
    return json.dumps({"id":case.id,"input_paths":case.input_paths,"expected_metrics":case.expected_metrics,"expected_nets":case.expected_nets,"notes":case.notes},sort_keys=True,indent=2)
