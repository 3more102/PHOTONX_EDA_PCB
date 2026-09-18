def connector_path_report(items):return [{"connector":x.connector_id,"target":x.target_id,"hops":x.hops,"confidence":x.confidence,"nodes":list(x.nodes)} for x in items]
