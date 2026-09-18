from photonx_eda_pcb.functional_blocks.model import FunctionalBlock
from photonx_eda_pcb.schematic_pages import generate_pages,validate_page_set
from photonx_eda_pcb.schematic_pages.index import component_page_index
def test_page_generation_split():
    b=FunctionalBlock("b",tuple(f"U{i}" for i in range(5)),("N1",),"compute",.8)
    ps=generate_pages([b],max_components=2)
    assert len(ps.pages)==3 and component_page_index(ps)["U4"]==("b:p3",)
    assert validate_page_set(ps)==[]
