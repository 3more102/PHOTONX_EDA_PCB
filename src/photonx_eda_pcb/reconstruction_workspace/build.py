def build_workspace_view(*,schematic_graph,blocks=(),pages=None,unresolved=(),review_queue=None):
    from .model import WorkspaceView
    return WorkspaceView(len(schematic_graph.components),len(schematic_graph.nets),len(list(blocks)),len(pages.pages) if pages is not None else 0,len(list(unresolved)),len(review_queue.items) if review_queue is not None else 0)
