DEFAULT_SHORTCUTS={"select":"S","pan":"Space","zoom_fit":"F","undo":"Ctrl+Z","redo":"Ctrl+Y","measure":"M"}
def shortcut_for(action,mapping=None):return (mapping or DEFAULT_SHORTCUTS).get(action)
