def match_components_to_hypotheses(assembly,hypotheses):
    by_ref={getattr(h,"reference",None):h for h in hypotheses if getattr(h,"reference",None)}
    return {c.reference:by_ref.get(c.reference) for c in assembly.components}
