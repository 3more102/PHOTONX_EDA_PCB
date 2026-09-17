class StageRegistry:
    def __init__(self):self._stages={}
    def register(self,stage):
        if stage.name in self._stages:raise ValueError(f'duplicate stage {stage.name}')
        self._stages[stage.name]=stage;return stage
    def get(self,name):return self._stages[name]
    def ordered(self):return [self._stages[k] for k in sorted(self._stages)]
