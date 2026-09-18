from pathlib import PurePosixPath
def module_key(path):
    p=PurePosixPath(str(path));parts=list(p.parts)
    if parts[-1]=="__init__.py":parts=parts[:-1]
    elif parts[-1].endswith(".py"):parts[-1]=parts[-1][:-3]
    return ".".join(parts)
def package_file_collisions(paths):
    files=set(str(x) for x in paths);out=[]
    for p in sorted(files):
        if not p.endswith(".py") or p.endswith("/__init__.py"):continue
        package=p[:-3]+"/__init__.py"
        if package in files:out.append((p,package))
    return out
