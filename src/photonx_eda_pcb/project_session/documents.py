def open_document(session,path):
    p=str(path)
    if p not in session.open_documents:session.open_documents.append(p)
    session.active_board=p
    return session
def close_document(session,path):
    p=str(path)
    session.open_documents=[x for x in session.open_documents if x!=p]
    if session.active_board==p:session.active_board=session.open_documents[-1] if session.open_documents else None
    return session
