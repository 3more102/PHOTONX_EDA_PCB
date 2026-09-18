def root_rails(dependencies):
    upstream={x.upstream for x in dependencies};downstream={x.downstream for x in dependencies}
    return tuple(sorted(upstream-downstream))
