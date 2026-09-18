class StatusController:
    def __init__(self):self.message="";self.level="info"
    def set(self,message,level="info"):self.message=str(message);self.level=str(level);return self
    def clear(self):self.message="";self.level="info";return self
