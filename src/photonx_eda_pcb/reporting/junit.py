from xml.etree.ElementTree import Element,SubElement,tostring
from ..checks import run_all_checks
def checks_to_junit(board)->str:
    issues=run_all_checks(board); suite=Element("testsuite",name="photonx_checks",tests=str(len(issues) or 1),failures=str(sum(i.severity=="error" for i in issues)))
    if not issues: SubElement(suite,"testcase",name="board_checks")
    for i in issues:
        case=SubElement(suite,"testcase",name=i.code)
        if i.severity=="error": SubElement(case,"failure",message=i.message)
    return tostring(suite,encoding="unicode")
