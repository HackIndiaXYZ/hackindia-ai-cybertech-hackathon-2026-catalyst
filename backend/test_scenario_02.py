from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_02.json"
)

raw_events = load_events(scenario_file)
events = normalize_events(raw_events)

relationships = build_sequence(events)

print("\nTRACE v1.2 BENIGN SCENARIO")
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

# These events share context but should not form
# a suspicious behavioral chain.
assert (
    "BEN-002",
    "BEN-005"
) not in actual_relationships

assert (
    "BEN-005",
    "BEN-004"
) not in actual_relationships

# Heartbeats must remain unconnected.
for relationship in relationships:
    assert relationship["event_a"] not in {
        "BEN-003",
        "BEN-006"
    }

    assert relationship["event_b"] not in {
        "BEN-003",
        "BEN-006"
    }

print("\n✓ Shared context did not create a false long-range correlation")
print("✓ HEARTBEAT events remain unconnected")
print("\nTRACE v1.2 BENIGN SCENARIO PASSED")
print("=" * 65)