def dataset_stats(m):
    files=[f for c in m.cases for f in c.files]
    return {"cases":len(m.cases),"files":len(files),"bytes":sum(f.bytes for f in files),"synthetic_cases":sum(c.synthetic for c in m.cases),"external_cases":sum(not c.synthetic for c in m.cases)}
