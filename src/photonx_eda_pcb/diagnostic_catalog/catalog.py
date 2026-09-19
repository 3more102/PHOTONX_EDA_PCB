class DiagnosticCatalog:
    def __init__(self):
        self._items = {}

    def add(self, item):
        if item.code in self._items:
            raise ValueError(f"duplicate diagnostic: {item.code}")
        self._items[item.code] = item
        return item

    def get(self, code):
        return self._items[str(code)]

    def get_optional(self, code):
        return self._items.get(str(code))

    def contains(self, code):
        return str(code) in self._items

    def find(self, text):
        q = str(text).lower()
        return [
            item
            for item in self.all()
            if q in item.code.lower()
            or q in item.title.lower()
            or q in item.description.lower()
        ]

    def all(self):
        return [self._items[key] for key in sorted(self._items)]

    def unknown_codes(self, codes):
        return tuple(sorted({str(code) for code in codes if not self.contains(code)}))
