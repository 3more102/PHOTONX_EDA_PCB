def centroid_summary(records):
    return {"count":len(records),"top":sum(r.side in {"top","front","f"} for r in records),"bottom":sum(r.side in {"bottom","back","b"} for r in records)}
