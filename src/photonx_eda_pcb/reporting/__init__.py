from .summary import build_summary
from .markdown import render_markdown_report
from .text import render_text_report

def summary(board,report=None):
    """Compatibility facade for the legacy reporting.summary() API."""
    data={"tracks":len(board.tracks),"pads":len(board.pads),"drills":len(board.drills),"slots":len(getattr(board,"slots",())),"outline_segments":len(board.outline),"physical_nets":len(board.nets),"component_hypotheses":len(board.components),"parse_diagnostics":len(board.diagnostics)}
    if report is not None:
        data.update({"validation_ok":report.ok,"errors":len(report.errors),"warnings":len(report.warnings)})
    return data

__all__=["build_summary","render_markdown_report","render_text_report","summary"]
