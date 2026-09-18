def grid_expected(rows,cols):
    rows=int(rows);cols=int(cols)
    return {"pads":rows*cols,"tracks":rows*max(0,cols-1)}
