import csv,io

def testpoints_csv(items):
    s=io.StringIO(); w=csv.writer(s); w.writerow(['object_id','net_id','diameter_mm','confidence'])
    for t in items:w.writerow([t.object_id,t.net_id or '',t.diameter_mm,t.confidence])
    return s.getvalue()
