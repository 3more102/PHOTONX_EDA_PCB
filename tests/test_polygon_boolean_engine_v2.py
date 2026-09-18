from photonx_eda_pcb.polygon_boolean import union_polygons,intersect_polygons,subtract_polygons,polygon_area
def test_boolean_engine_rectangles():
    a=((0,0),(2,0),(2,2),(0,2));b=((1,0),(3,0),(3,2),(1,2))
    u=union_polygons([a,b]);i=intersect_polygons(a,b);d=subtract_polygons(a,b)
    assert round(sum(polygon_area(x) for x in u),6)==6
    assert round(sum(polygon_area(x) for x in i),6)==2
    assert round(sum(polygon_area(x) for x in d),6)==2
