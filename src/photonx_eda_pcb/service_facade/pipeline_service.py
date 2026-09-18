class PipelineService:
    def execute(self,dag,initial=None,cache=None,version="1"):
        from photonx_eda_pcb.pipeline_dag.executor import execute_dag
        return execute_dag(dag,initial,cache,version)
