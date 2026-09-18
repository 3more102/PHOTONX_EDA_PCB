class GroundTruthRegistry:
    def __init__(self):self._cases={}
    def add(self,case):
        if case.id in self._cases:raise ValueError("duplicate ground truth case")
        self._cases[case.id]=case
    def all(self):return [self._cases[k] for k in sorted(self._cases)]
