class ProjectController:
    def __init__(self,session):self.session=session
    def set_active(self,path):
        from photonx_eda_pcb.project_session.documents import open_document
        open_document(self.session,path);return self.session.active_board
    def close(self,path):
        from photonx_eda_pcb.project_session.documents import close_document
        close_document(self.session,path);return self.session.active_board
