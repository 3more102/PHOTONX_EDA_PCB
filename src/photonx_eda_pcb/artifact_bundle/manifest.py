def bundle_manifest(bundle):
    return {"name":bundle.name,"entries":[{"path":e.path,"role":e.role,"sha256":e.sha256} for e in bundle.entries],"metadata":dict(bundle.metadata)}
