def orphan_modules(modules,imports,public_modules=()):
    mods=set(map(str,modules));used=set(map(str,public_modules))
    for src,targets in imports.items():
        if src in mods:used.add(src)
        used.update(t for t in targets if t in mods)
    return sorted(mods-used)
