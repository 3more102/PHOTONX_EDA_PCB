from dataclasses import dataclass
@dataclass(frozen=True)
class UiAction:
    id:str
    label:str
    shortcut:str=""
    enabled:bool=True
DEFAULT_ACTIONS=(UiAction("open","Open","Ctrl+O"),UiAction("save","Save","Ctrl+S"),UiAction("undo","Undo","Ctrl+Z"),UiAction("redo","Redo","Ctrl+Y"),UiAction("zoom_fit","Zoom Fit","F"),UiAction("validate","Validate","Ctrl+Shift+V"))
