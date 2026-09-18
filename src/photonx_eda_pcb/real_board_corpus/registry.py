class CorpusRegistry:
    def __init__(self):self._cases={}
    def add(self,case):
        if case.id in self._cases:raise ValueError(f"duplicate corpus case: {case.id}")
        self._cases[case.id]=case
    def get(self,case_id):return self._cases[case_id]
    def ids(self):return sorted(self._cases)
