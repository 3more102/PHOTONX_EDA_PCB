def build_release_candidate(name,commit,artifacts,metadata=None):
    from .model import ReleaseCandidate
    return ReleaseCandidate(str(name),str(commit),sorted(list(artifacts),key=lambda x:str(getattr(x,"path",getattr(x,"name","")))),dict(metadata or {}))
