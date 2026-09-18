def audit_markdown(report):
    lines=["# Release Audit","","| Check | Passed | Details |","|---|---|---|"]
    lines += [f"| {c.name} | {'yes' if c.passed else 'no'} | {c.details} |" for c in report.checks]
    return "\n".join(lines)+"\n"
