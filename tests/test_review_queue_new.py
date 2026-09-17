from photonx_eda_pcb.review_queue import ReviewItem,ReviewQueue
from photonx_eda_pcb.review_queue.decisions import apply_decision
def test_review_queue_orders_low_confidence_first():
    queue=ReviewQueue(); queue.add(ReviewItem('a','component','U1','ambiguous',0.7)); queue.add(ReviewItem('b','net','N1','conflict',0.2))
    assert [item.id for item in queue.open_items()]==['b','a']
    apply_decision(queue.get('b'),'accept'); assert queue.get('b').status=='resolved'
