def migrate_payload(payload,target_version,registry):
    cur=dict(payload);seen=set()
    version=int(cur.get("schema_version",1))
    while version<int(target_version):
        if version in seen:raise RuntimeError("migration cycle")
        seen.add(version)
        m=registry.next_from(version)
        if m is None or m.to_version>target_version:raise ValueError(f"no migration from {version} to {target_version}")
        cur=m.fn(dict(cur));version=m.to_version;cur["schema_version"]=version
    if version!=int(target_version):raise ValueError("cannot downgrade payload")
    return cur
