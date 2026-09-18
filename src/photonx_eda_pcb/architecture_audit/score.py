WEIGHT={"info":1,"warning":3,"error":8,"critical":16}
def technical_debt_score(audit):return sum(WEIGHT.get(x.severity,3) for x in audit.findings)
