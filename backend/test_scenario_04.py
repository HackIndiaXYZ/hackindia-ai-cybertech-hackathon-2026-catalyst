from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_04.json"
)

raw_events = load_events(scenario_file)
events = normalize_events(raw_events)

relationships = build_sequence(events)

print("\nTRACE v1.4 OUT-OF-ORDER TELEMETRY")
print("=" * 65)

for relationship in relationships:
    print(
        f"{relationship['event_a']} → "
        f"{relationship['event_b']} | "
        f"{relationship['event_type_a']} → "
        f"{relationship['event_type_b']} | "
        f"score: {relationship['score']}"
    )


actual_relationships = {
    (
        relationship["event_a"],
        relationship["event_b"]
    )
    for relationship in relationships
}


expected_relationships = {
    ("OOO-001", "OOO-002"),
    ("OOO-002", "OOO-004"),
    ("OOO-004", "OOO-005"),
    ("OOO-005", "OOO-006")
}


for expected in expected_relationships:
    assert expected in actual_relationships, (
        f"Missing expected relationship: {expected}"
    )


# Heartbeat must remain unconnected.

for relationship in relationships:
    assert relationship["event_a"] != "OOO-003"
    assert relationship["event_b"] != "OOO-003"


print("\n✓ Events reconstructed using timestamps")
print("✓ Input ordering did not affect reconstruction")
print("✓ HEARTBEAT remained unconnected")
print("✓ Correct behavioral chain reconstructed")

print("\nTRACE v1.4 OUT-OF-ORDER TEST PASSED")
print("=" * 65)