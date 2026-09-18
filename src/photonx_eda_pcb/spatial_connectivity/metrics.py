def spatial_metrics(index):
    occupancies=[len(v) for v in index._cells.values()]
    return {"objects":len(index),"cells":len(index._cells),"max_cell_occupancy":max(occupancies,default=0),"mean_cell_occupancy":0.0 if not occupancies else round(sum(occupancies)/len(occupancies),6)}
