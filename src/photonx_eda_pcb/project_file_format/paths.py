from pathlib import PurePosixPath
def normalize_project_path(path):
    p=PurePosixPath(str(path).replace("\\","/"))
    if p.is_absolute() or ".." in p.parts:raise ValueError("project paths must be relative")
    return str(p)
