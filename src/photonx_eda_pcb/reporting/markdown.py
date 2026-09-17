from .summary import build_summary
from ..checks import run_all_checks
def render_markdown_report(board)->str:
    s=build_summary(board); issues=run_all_checks(board)
    lines=["# PHOTONX Reconstruction Report","",f"- Completeness: {s['completeness']:.2%}",f"- Quality: {s['quality']:.2%}","","## Object counts"]
    for k,v in s["stats"].items(): lines.append(f"- {k}: {v}")
    lines.extend(["","## Checks"]); lines += [f"- **{i.severity.upper()} {i.code}**: {i.message}" for i in issues] or ["- No check findings."]
    return "\n".join(lines)+"\n"
