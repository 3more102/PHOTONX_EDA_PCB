from collections import Counter
from .base import RuleIssue


def _source_pin_map_issues(component):
    out = []
    pad_ids = set(component.pad_ids)
    pin_map = getattr(component, 'source_pin_map', {})
    pin_functions = getattr(component, 'source_pin_functions', {})

    if not isinstance(pin_map, dict):
        return [
            RuleIssue(
                'error',
                'COMPONENT_PIN_MAP_INVALID',
                'source pin map must be a dictionary',
                component.id,
            )
        ]
    if not isinstance(pin_functions, dict):
        out.append(
            RuleIssue(
                'error',
                'COMPONENT_PIN_FUNCTION_MAP_INVALID',
                'source pin function map must be a dictionary',
                component.id,
            )
        )
        pin_functions = {}

    for pad_id, pin_number in sorted(pin_map.items()):
        if pad_id not in pad_ids:
            out.append(
                RuleIssue(
                    'error',
                    'COMPONENT_PIN_MAP_PAD_NOT_MEMBER',
                    f'source pin map references non-member pad {pad_id}',
                    component.id,
                )
            )
        if not isinstance(pin_number, str) or not pin_number.strip():
            out.append(
                RuleIssue(
                    'error',
                    'COMPONENT_PIN_NUMBER_INVALID',
                    f'invalid source pin number for pad {pad_id}',
                    component.id,
                )
            )

    for pad_id, pin_function in sorted(pin_functions.items()):
        if pad_id not in pin_map:
            out.append(
                RuleIssue(
                    'error',
                    'COMPONENT_PIN_FUNCTION_PAD_NOT_MAPPED',
                    f'source pin function references pad without source pin number {pad_id}',
                    component.id,
                )
            )
        if not isinstance(pin_function, str) or not pin_function.strip():
            out.append(
                RuleIssue(
                    'error',
                    'COMPONENT_PIN_FUNCTION_INVALID',
                    f'invalid source pin function for pad {pad_id}',
                    component.id,
                )
            )

    return out


def valid_component_references(board):
    pads={p.id for p in getattr(board,'pads',[])}; out=[]
    components=list(getattr(board,'components',[]))
    component_id_counts=Counter(c.id for c in components)
    for component_id,count in sorted(component_id_counts.items()):
        if count>1: out.append(RuleIssue('error','DUPLICATE_COMPONENT_ID',f'duplicate component hypothesis id {component_id}',component_id))
    for c in components:
        duplicate_pad_ids=sorted(pid for pid,count in Counter(c.pad_ids).items() if count>1)
        if duplicate_pad_ids: out.append(RuleIssue('error','COMPONENT_PAD_DUPLICATE',f'duplicate pad ids {duplicate_pad_ids}',c.id))
        if not 0<=c.confidence<=1: out.append(RuleIssue('error','COMPONENT_CONFIDENCE','component confidence outside [0,1]',c.id))
        for pid in c.pad_ids:
            if pid not in pads: out.append(RuleIssue('error','COMPONENT_PAD_MISSING',f'unknown pad {pid}',c.id))
        out.extend(_source_pin_map_issues(c))
    return out
