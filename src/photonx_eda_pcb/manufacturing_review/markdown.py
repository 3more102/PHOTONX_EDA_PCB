def to_markdown(report):
    lines=["# Manufacturing Review","","| Severity | Code | Message |","|---|---|---|"]
    lines += [f"| {f.severity} | {f.code} | {f.message.replace('|','/')} |" for f in report.findings]
    return "\n".join(lines)+"\n"
