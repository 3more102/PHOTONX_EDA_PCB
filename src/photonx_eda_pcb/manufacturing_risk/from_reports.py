from .model import RiskItem
def from_dfm(report):
    sev={"info":.1,"warning":.35,"error":.7,"critical":1.0}
    return [RiskItem("assembly",f.code,sev.get(f.severity,.35),f.severity) for f in report.findings]
def from_keepouts(violations):
    return [RiskItem("mechanical","KEEPOUT",.6,"error") for _ in violations]
