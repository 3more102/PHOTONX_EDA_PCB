import json
def unified_markdown(report):
    lines=["# "+report.title,""]
    for s in report.sections:
        lines.extend(["## "+s.name,"",json.dumps(s.payload,sort_keys=True,indent=2,default=str),""])
    return "\n".join(lines)
