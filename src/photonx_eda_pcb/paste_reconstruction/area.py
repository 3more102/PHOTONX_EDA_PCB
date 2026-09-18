def aperture_area(a):return float(a.size[0])*float(a.size[1])
def total_paste_area(apertures):return sum(aperture_area(a) for a in apertures)
