def markdown_report(results):
    lines=['# Regression report','',f'Cases: {len(results)}','']
    for r in results: lines.append(f"- {'PASS' if r.passed else 'FAIL'} — {r.name}")
    return '\n'.join(lines)+'\n'
