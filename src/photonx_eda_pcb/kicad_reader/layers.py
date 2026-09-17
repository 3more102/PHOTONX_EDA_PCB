from .query import children
def read_layers(root):
    table=[]
    for node in children(root,'layers'):
        for row in node[1:]:
            if isinstance(row,list) and len(row)>=3: table.append({'id':row[0],'name':str(row[1]),'type':str(row[2])})
    return table
