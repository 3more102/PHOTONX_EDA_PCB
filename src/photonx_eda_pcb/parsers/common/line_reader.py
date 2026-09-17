def iter_nonempty_lines(text:str):
    for number,line in enumerate(text.splitlines(),start=1):
        stripped=line.strip()
        if stripped: yield number,stripped
