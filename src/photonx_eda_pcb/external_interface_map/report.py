def interface_map_report(m):return {"connectors":m.connectors,"ports":[x.__dict__ for x in m.ports],"protection_count":len(m.protection),"confidence":m.confidence,"unresolved":list(m.unresolved)}
