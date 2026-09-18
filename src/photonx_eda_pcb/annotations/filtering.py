def find_annotations(store,*,category=None,author=None,resolved=None,text=""):
    q=str(text).lower()
    return [x for x in store.items if (category is None or x.category==category) and (author is None or x.author==author) and (resolved is None or x.resolved==resolved) and (not q or q in x.text.lower())]
