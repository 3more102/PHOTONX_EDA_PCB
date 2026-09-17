from types import SimpleNamespace as NS
from photonx_eda_pcb.cli_commands.inspect_cmd import inspect_board
from photonx_eda_pcb.cli_commands.export_cmd import check_export_request
def test_inspect():
 b=NS(tracks=[1],pads=[1,2],drills=[],outline=[],nets=[],components=[]); assert inspect_board(b).data['pads']==2
def test_export_suffix_warning(): assert check_export_request('board.txt','kicad').data['issues']
