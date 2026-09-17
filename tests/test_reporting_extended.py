from photonx_eda_pcb.models import *
from photonx_eda_pcb.reporting.markdown import render_markdown_report
from photonx_eda_pcb.reporting.text import render_text_report
from photonx_eda_pcb.reporting.json_report import render_json_report
from photonx_eda_pcb.reporting.csv_tables import nets_csv
from photonx_eda_pcb.reporting.junit import checks_to_junit
def test_reports_are_serializable():
 b=BoardModel(metadata={"units":"mm"},nets=[NetGroup("N0",[],.8)])
 assert "PHOTONX" in render_markdown_report(b); assert "PHOTONX report" in render_text_report(b); assert '"quality"' in render_json_report(b); assert "net_id" in nets_csv(b); assert "testsuite" in checks_to_junit(b)
