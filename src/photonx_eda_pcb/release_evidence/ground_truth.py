def ground_truth_passed(results):return all(getattr(x,"passed",False) for x in results)
