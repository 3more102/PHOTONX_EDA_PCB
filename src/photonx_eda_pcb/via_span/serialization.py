from dataclasses import asdict
def spans_to_dict(spans): return [asdict(x) for x in spans]
