def readiness_dashboard(r):
    from photonx_eda_pcb.quality_dashboard.build import build_dashboard
    return build_dashboard({"phase70":{"score":r.score,"passed":r.passed,"blockers":list(r.blockers)}})
