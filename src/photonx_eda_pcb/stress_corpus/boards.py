from photonx_eda_pcb.models import BoardModel,PadCandidate,Point,Track
def grid_board(rows=20,cols=20,pitch_mm=2.0,pad_mm=.8,layer="F.Cu"):
    pads=[];tracks=[]
    for r in range(int(rows)):
        for c in range(int(cols)):
            x=c*pitch_mm;y=r*pitch_mm;pid=f"P{r}_{c}"
            pads.append(PadCandidate(pid,Point(x,y),pad_mm,pad_mm,"C",layer))
            if c+1<int(cols):
                tracks.append(Track(f"T{r}_{c}",Point(x,y),Point((c+1)*pitch_mm,y),.2,layer))
    return BoardModel(tracks=tracks,pads=pads)
def clustered_board(clusters=10,cluster_size=20,spacing_mm=10.0,local_pitch_mm=.4,layer="F.Cu"):
    pads=[]
    for k in range(int(clusters)):
        base=k*spacing_mm
        for i in range(int(cluster_size)):
            x=base+(i%5)*local_pitch_mm;y=(i//5)*local_pitch_mm
            pads.append(PadCandidate(f"C{k}_{i}",Point(x,y),.3,.3,"C",layer))
    return BoardModel(pads=pads)
