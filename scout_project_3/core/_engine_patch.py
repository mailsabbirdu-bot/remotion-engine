import os, time

def sanitize_query(query):
    if isinstance(query, dict):
        query = query.get("text") or query.get("query") or "ocean"
    return str(query)[:100]

def safe_int(x):
    if isinstance(x, dict):
        return sum(x.values())
    return int(x)

def wait_for_file(path, timeout=20):
    for _ in range(timeout*2):
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return True
        time.sleep(0.5)
    return False
