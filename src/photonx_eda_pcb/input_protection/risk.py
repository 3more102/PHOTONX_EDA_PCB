def unprotected_connectors(connector_ids,paths):
    covered={x.connector_id for x in paths}
    return tuple(sorted(set(map(str,connector_ids))-covered))
