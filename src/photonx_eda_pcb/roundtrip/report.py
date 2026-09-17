def render_roundtrip_report(diffs):
    if not diffs:return '# Round-trip report\n\nPASS: canonical board models match.\n'
    lines=['# Round-trip report','','FAIL: canonical model differences detected.','']
    lines += [f"- {d['section']}: {d['left_count']} vs {d['right_count']}" for d in diffs]
    return '\n'.join(lines)+'\n'
