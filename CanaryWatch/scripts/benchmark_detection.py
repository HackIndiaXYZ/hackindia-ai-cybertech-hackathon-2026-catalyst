import statistics, time, urllib.request, urllib.error, json, sys

BASE = "http://127.0.0.1:8000/api/v1"

def request(path, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, data=body,
        headers={"Content-Type": "application/json"}, method="GET" if data is None else "POST")
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode())

try:
    request("/demo/start", {})
    tokens = request("/honeytokens")
    samples = []
    for token in tokens:
        if token["status"] == "active":
            result = request(f"/demo/trigger/{token['id']}", {})
            samples.append(result["measured_latency_ms"])
    if not samples:
        print("No active demo tokens found. Reset demo and run again.")
        sys.exit(1)
    ordered = sorted(samples)
    p95 = ordered[min(int((len(ordered)-1)*.95), len(ordered)-1)]
    print("CanaryWatch local demo benchmark")
    print(f"Sample count: {len(samples)}")
    print(f"Min backend processing: {min(samples):.3f} ms")
    print(f"Median backend processing: {statistics.median(samples):.3f} ms")
    print(f"P95 backend processing: {p95:.3f} ms")
    print(f"Max backend processing: {max(samples):.3f} ms")
    print("Note: this measures local backend processing only, not end-to-end network or real-world breach detection.")
except Exception as exc:
    print(f"Benchmark failed: {exc}")
    print("Start the backend first: uvicorn app.main:app --reload")
    sys.exit(1)
