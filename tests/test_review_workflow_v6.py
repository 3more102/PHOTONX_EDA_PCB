from photonx_eda_pcb.review_workflow import ReviewItem,ReviewQueue,enqueue,next_item,accept,validate_queue
def test_review_priority_and_decision():
    q=ReviewQueue();enqueue(q,ReviewItem("a","value_hypothesis","R1",20));enqueue(q,ReviewItem("b","unsupported_syntax","file",100))
    x=next_item(q);assert x.id=="b"
    accept(x,"checked");assert x.status=="closed" and x.decision=="accepted"
    assert validate_queue(q)==[]
