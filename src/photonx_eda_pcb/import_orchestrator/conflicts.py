def format_conflicts(results):
    return [r for r in results if any(str(d).startswith("FORMAT_MISMATCH") for d in r.diagnostics)]
