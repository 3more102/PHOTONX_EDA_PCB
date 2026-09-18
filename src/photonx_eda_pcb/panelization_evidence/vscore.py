def vscore_candidate(line_length_mm,board_span_mm,angle_deg):
    if board_span_mm<=0:return 0.0
    length_score=min(1.0,float(line_length_mm)/float(board_span_mm))
    angle_score=1.0 if min(abs(angle_deg%180),abs((angle_deg%180)-90))<2 else 0.0
    return round(0.7*length_score+0.3*angle_score,6)
