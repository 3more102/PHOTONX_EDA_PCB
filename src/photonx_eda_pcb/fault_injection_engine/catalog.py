def board_faults():
    from .model import Fault
    return [Fault("remove-outline","clear_list","outline"),Fault("duplicate-pad","duplicate_list_item","pads",0),Fault("remove-net","clear_list","nets")]
