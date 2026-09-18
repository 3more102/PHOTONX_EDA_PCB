def decision_markdown(d):
    cons="\n".join("- "+x for x in d.consequences) or "- None recorded"
    return "# "+d.id+": "+d.title+"\n\nStatus: "+d.status+"\n\n## Context\n\n"+d.context+"\n\n## Decision\n\n"+d.decision+"\n\n## Consequences\n\n"+cons+"\n"
