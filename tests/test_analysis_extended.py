from photonx_eda_pcb.models import *
from photonx_eda_pcb.analysis.board_stats import board_stats
from photonx_eda_pcb.analysis.completeness import completeness_score
from photonx_eda_pcb.analysis.net_metrics import net_member_counts
from photonx_eda_pcb.analysis.drill_metrics import unknown_plating_count
from photonx_eda_pcb.analysis.topology import orphan_pad_ids
def board():
 b=BoardModel(); b.tracks=[Track("T0",Point(0,0),Point(1,0),.2,"F.Cu","N0")]; b.pads=[PadCandidate("P0",Point(0,0),1,1,"C","F.Cu",net_id="N0"),PadCandidate("P1",Point(2,0),1,1,"C","F.Cu")]; b.drills=[DrillHit("D0",Point(0,0),.5)]; b.nets=[NetGroup("N0",["T0","P0"],.9)]; return b
def test_stats_and_metrics():
 b=board(); assert board_stats(b)["tracks"]==1; assert net_member_counts(b)=={"N0":2}; assert unknown_plating_count(b)==1; assert orphan_pad_ids(b)==["P1"]; assert completeness_score(b)>0
