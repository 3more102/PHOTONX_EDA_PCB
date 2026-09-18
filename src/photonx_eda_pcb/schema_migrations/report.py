def migration_report(before,after):
    return {"from":int(before.get("schema_version",1)),"to":int(after.get("schema_version",1)),"added_keys":sorted(set(after)-set(before)),"removed_keys":sorted(set(before)-set(after))}
