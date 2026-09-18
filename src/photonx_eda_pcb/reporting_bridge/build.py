from .model import UnifiedReport,ReportSection
def build_unified_report(title,sections):
    return UnifiedReport(str(title),[ReportSection(str(name),payload) for name,payload in sorted(sections.items())])
