def index_correspondence(a,b):
    n=min(len(a),len(b));return list(zip(a[:n],b[:n]))
