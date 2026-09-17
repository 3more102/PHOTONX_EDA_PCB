from .common import CommandResult
from ..validation_rules import builtin_registry
def validate_board_rules(board):
    issues=builtin_registry().run(board); errors=[i for i in issues if i.severity=='error']
    return CommandResult(1 if errors else 0,f'{len(issues)} validation issue(s)',{'errors':len(errors),'issues':[i.__dict__ for i in issues]})
