MAX_FUZZ_INPUT_BYTES=1_000_000
MAX_CASES_PER_RUN=10_000

def within_limits(payload,cases=1):return len(payload.encode('utf-8'))<=MAX_FUZZ_INPUT_BYTES and cases<=MAX_CASES_PER_RUN
