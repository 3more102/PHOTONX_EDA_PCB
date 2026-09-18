class QueryService:
    def parse(self,text):
        from photonx_eda_pcb.query_engine.parser import parse_query
        return parse_query(text)
    def execute(self,items,query):
        from photonx_eda_pcb.query_engine.engine import execute_query
        return execute_query(items,query)
