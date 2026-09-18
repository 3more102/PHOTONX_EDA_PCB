def low_quality(items,threshold=.5):return [x for x in items if x.score<float(threshold)]
