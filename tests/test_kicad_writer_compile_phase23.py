from photonx_eda_pcb.kicad_schematic_export.model import ExportDocument
from photonx_eda_pcb.kicad_schematic_export.writer import write_export_document

def test_writer_imports_and_emits_root_sheet_instance():
    text=write_export_document(ExportDocument(project_name="Demo",root_uuid="00000000-0000-0000-0000-000000000001"))
    assert '(sheet_instances (path "/" (page "1")))' in text
