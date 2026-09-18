class SourceAdapter:
    format_name="unknown"
    def can_read(self,guess):return guess.format==self.format_name
    def read(self,path,text):raise NotImplementedError
