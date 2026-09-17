from pathlib import Path
def normalized_path(path:str|Path)->str: return Path(path).as_posix()
def extension(path:str|Path)->str: return Path(path).suffix.lower()
