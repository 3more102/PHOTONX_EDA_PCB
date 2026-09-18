from .model import DagRunResult
from .order import topological_order
from .fingerprint import node_fingerprint
def execute_dag(dag,initial=None,cache=None,version="1",stop_on_error=True):
    artifacts=dict(initial or {});result=DagRunResult(artifacts)
    for name in topological_order(dag):
        node=dag.nodes[name]
        missing=[r for r in node.requires if r not in artifacts]
        if missing:
            result.skipped.append(name);continue
        inputs={r:artifacts[r] for r in node.requires}
        key=node_fingerprint(node,inputs,version)
        cached=cache.get(key,None) if cache is not None and node.cacheable else None
        if cached is not None:
            if isinstance(cached,dict):artifacts.update(cached)
            result.skipped.append(name);continue
        try:
            produced=node.fn(dict(inputs))
            if produced is None:produced={}
            if not isinstance(produced,dict):raise TypeError("DAG node must return dict")
            artifacts.update(produced);result.executed.append(name)
            if cache is not None and node.cacheable:cache.put(key,dict(produced))
        except Exception as exc:
            result.failed.append((name,f"{type(exc).__name__}: {exc}"))
            if stop_on_error:break
    return result
