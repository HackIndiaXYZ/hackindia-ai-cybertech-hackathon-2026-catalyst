from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from incident import build_incident


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


raw_events = load_events(scenario_file)

events = normalize_events(
    raw_events
)

relationships = build_sequence(
    events
)

incident = build_incident(
    events,
    relationships
)


print("\nTRACE v0.6 INCIDENT ANALYSIS")
print("=" * 60)

print(
    f"Incident ID: "
    f"{incident['incident_id']}"
)

print(
    f"Severity: "
    f"{incident['severity']}"
)

print(
    f"Risk score: "
    f"{incident['risk_score']}"
)

print(
    f"Events involved: "
    f"{incident['event_count']}"
)

print("\nINDICATORS")
print("-" * 60)

for indicator in incident["indicators"]:

    print(
        f"✓ {indicator}"
    )

print("\nRECONSTRUCTED RELATIONSHIPS")
print("-" * 60)

for relationship in incident["relationships"]:

    print(
        f"{relationship['source']}"
        f" → "
        f"{relationship['target']}"
        f" | score: "
        f"{relationship['score']}"
    )


assert incident["event_count"] > 0

assert 0 <= incident["risk_score"] <= 1

assert incident["severity"] in {
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH"
}

print("\n✓ Incident structure valid")
print("✓ Risk score within valid range")
print("✓ Severity classification valid")

print("\nTRACE v0.6 INCIDENT TEST PASSED")
print("=" * 60)