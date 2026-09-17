from dataclasses import asdict
def workspace_snapshot(state):
    value=asdict(state); value["metadata"]=dict(sorted(value["metadata"].items())); return value
