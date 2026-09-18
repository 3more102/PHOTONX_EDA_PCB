from pathlib import PurePosixPath
def duplicate_leaf_modules(paths):
    by={}
    for p in paths:
        x=PurePosixPath(str(p))
        if x.suffix!=".py":continue
        leaf=x.stem
        if leaf=="__init__":continue
        by.setdefault(leaf,[]).append(str(p))
    return {k:tuple(sorted(v)) for k,v in by.items() if len(v)>1}
