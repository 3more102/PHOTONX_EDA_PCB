from photonx_eda_pcb.review_workflow.model import ReviewItem,ReviewQueue
from photonx_eda_pcb.review_workflow.filtering import filter_items
def test_review_filter():
    q=ReviewQueue([ReviewItem("1","x","a",status="open",assignee="omar"),ReviewItem("2","y","b",status="closed")])
    assert [x.id for x in filter_items(q,status="open",assignee="omar")]==["1"]
