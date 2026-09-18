def add_net_labels(schematic,labels,origin=(0.0,0.0),step=5.0):
    x,y=origin
    for i,(net_id,label) in enumerate(sorted(labels.items())):
        schematic.labels.append((str(label or net_id),x,y+i*step))
    return schematic
