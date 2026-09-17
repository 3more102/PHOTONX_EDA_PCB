def summarize(board_dict): return {k:len(v) for k,v in board_dict.items() if isinstance(v,list)}
