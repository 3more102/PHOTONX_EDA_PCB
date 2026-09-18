CATEGORIES=("parser","geometry","connectivity","components","analog","power","protocol","schematic","export","corruption","performance")
def by_category(corpus,category):return [c for c in corpus.cases if c.category==category]
def by_tag(corpus,tag):return [c for c in corpus.cases if tag in c.tags]
