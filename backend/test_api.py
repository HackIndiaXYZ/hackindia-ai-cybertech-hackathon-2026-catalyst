from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


print()
print("TRACE v1.8 API TEST")
print("=" * 70)


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

response = client.get("/health")

assert response.status_code == 200

health = response.json()

assert health["status"] == "ok"
assert health["engine"] == "TRACE v1.8"

print("✓ Health endpoint passed")


# ------------------------------------------------------------
# SCENARIO TEST
# ------------------------------------------------------------

response = client.get(
    "/scenario/01"
)

assert response.status_code == 200

report = response.json()

assert report["trace"]["engine"] == "TRACE v1.7"

assert (
    report["summary"]["total_events"]
    == 10
)

assert (
    report["summary"]
    ["reconstructed_relationships"]
    == 5
)

assert (
    report["summary"]["incident_count"]
    == 3
)

print("✓ Scenario endpoint passed")


# ------------------------------------------------------------
# INVESTIGATION VALIDATION
# ------------------------------------------------------------

incidents = report["incidents"]

assert len(incidents) == 3

assert incidents[0]["incident_id"] == "INC-002"

assert incidents[0]["severity"] == "HIGH"

assert incidents[0]["risk_score"] == 0.96

assert len(
    incidents[0]["timeline"]
) == 4

assert len(
    incidents[0]["relationships"]
) == 3

print("✓ Investigation report returned correctly")


# ------------------------------------------------------------
# INVALID SCENARIO
# ------------------------------------------------------------

response = client.get(
    "/scenario/99"
)

assert response.status_code == 404

print("✓ Invalid scenario handled correctly")


# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print()
print("TRACE v1.8 API TEST PASSED")
print("=" * 70)