def edge_margins(board,enclosure):
    bx0,by0,bx1,by1=map(float,board);ex0,ey0,ex1,ey1=map(float,enclosure)
    return (bx0-ex0,by0-ey0,ex1-bx1,ey1-by1)
