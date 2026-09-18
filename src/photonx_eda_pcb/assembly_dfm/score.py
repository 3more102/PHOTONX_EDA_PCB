def dfm_score(report):
    penalty={"info":.01,"warning":.05,"error":.15,"critical":.3}
    return round(max(0.0,1-sum(penalty.get(f.severity,.05) for f in report.findings)),6)
