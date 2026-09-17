def by_prefix(cases,prefix): return [c for c in cases if c.name.startswith(prefix)]
def by_tag(cases,tag): return [c for c in cases if tag in c.tags]
