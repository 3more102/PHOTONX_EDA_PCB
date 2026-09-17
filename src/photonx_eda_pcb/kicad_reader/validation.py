def validate_board_dict(data):
    issues=[]
    if not data.get('edge_lines'): issues.append(('warning','KICAD_EDGE_MISSING'))
    codes=[n['code'] for n in data.get('nets',[])];
    if len(codes)!=len(set(codes)): issues.append(('error','KICAD_DUP_NET_CODE'))
    return issues
