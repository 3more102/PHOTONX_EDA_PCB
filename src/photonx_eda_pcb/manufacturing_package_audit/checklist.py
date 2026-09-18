def manufacturing_checklist(audit):
    return [{"item":"package blockers","passed":not audit.blockers},{"item":"production validation","passed":bool(audit.metrics.get("production_validation",True))},{"item":"source traceability","passed":audit.metrics.get("source_traceability",1)>=.95},{"item":"roundtrip fidelity","passed":audit.metrics.get("roundtrip_fidelity",1)>=.95}]
