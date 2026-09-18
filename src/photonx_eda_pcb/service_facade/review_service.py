class ReviewService:
    def next(self,queue):
        from photonx_eda_pcb.review_workflow.queue import next_item
        return next_item(queue)
    def summary(self,queue):
        from photonx_eda_pcb.review_workflow.report import queue_summary
        return queue_summary(queue)
