from dataclasses import dataclass,field
@dataclass
class Transaction:
    label:str
    changes:list=field(default_factory=list)
def apply_transaction(state,tx,stack):
    for c in tx.changes:stack.do(state,c)
    return state
