def select_jobs(jobs,commands=None,ids=None):
    commands=set(commands or []);ids=set(ids or [])
    return [j for j in jobs if (not commands or j.command in commands) and (not ids or j.id in ids)]
