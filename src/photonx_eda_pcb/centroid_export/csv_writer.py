import csv,io
FIELDS=("Reference","X_mm","Y_mm","Rotation_deg","Side","Footprint","Value")
def write_centroid_csv(records):
    s=io.StringIO(newline="");w=csv.writer(s,lineterminator="\n");w.writerow(FIELDS)
    for r in sorted(records,key=lambda x:x.reference):
        w.writerow([r.reference,f"{r.x_mm:.6f}",f"{r.y_mm:.6f}",f"{r.rotation_deg:.6f}",r.side,r.footprint,r.value])
    return s.getvalue()
