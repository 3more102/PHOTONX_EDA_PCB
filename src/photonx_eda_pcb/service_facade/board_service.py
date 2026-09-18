class BoardService:
    def stats(self,board):
        from photonx_eda_pcb.board_statistics.compute import compute_board_stats
        return compute_board_stats(board)
    def validate(self,board):
        from photonx_eda_pcb.validation import validate_board
        return validate_board(board)
