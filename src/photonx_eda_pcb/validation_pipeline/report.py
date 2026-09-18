def report_markdown(report):
    lines=["# Validation Pipeline","","| Check | Passed | Severity | Messages |","|---|---|---|---|"]
    for r in report.results:lines.append(f"| {r.name} | {'yes' if r.passed else 'no'} | {r.severity} | {'; '.join(r.messages).replace('|','/')} |")
    return "\n".join(lines)+"\n"
