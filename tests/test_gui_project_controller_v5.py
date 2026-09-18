from photonx_eda_pcb.project_session import ProjectSession
from photonx_eda_pcb.gui_controllers.project import ProjectController
def test_project_controller():
    c=ProjectController(ProjectSession("P"));assert c.set_active("x.kicad_pcb")=="x.kicad_pcb";assert c.close("x.kicad_pcb") is None
