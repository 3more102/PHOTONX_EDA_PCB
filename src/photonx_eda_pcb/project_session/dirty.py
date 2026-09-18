def mark_dirty(session):
    session.dirty=True;session.revision+=1;return session
def mark_saved(session):
    session.dirty=False;return session
