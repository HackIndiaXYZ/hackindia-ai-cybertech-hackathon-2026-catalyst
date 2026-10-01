from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_03.json"
)

raw_events = load_events(scenario_file)
events = normalize_events(raw_events)

relationships = build_sequence(events)

print("\nTRACE v1.3 ADVERSARIAL SCENARIO")
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


# --------------------------------------------------
# Expected legitimate relationships
# --------------------------------------------------

expected_relationships = {
    ("ADV-001", "ADV-002"),
    ("ADV-003", "ADV-004"),
    ("ADV-004", "ADV-005"),
    ("ADV-006", "ADV-007")
}


for expected in expected_relationships:
    assert expected in actual_relationships, (
        f"Missing expected relationship: {expected}"
    )


# --------------------------------------------------
# Relationships that MUST NOT exist
# --------------------------------------------------

forbidden_relationships = {
    ("ADV-002", "ADV-005"),
    ("ADV-001", "ADV-005"),
    ("ADV-003", "ADV-006")
}


for forbidden in forbidden_relationships:
    assert forbidden not in actual_relationships, (
        f"False correlation detected: {forbidden}"
    )


# --------------------------------------------------
# Ensure unrelated devices are not bridged
# --------------------------------------------------

assert not (
    ("ADV-002", "ADV-004")
    in actual_relationships
)

assert not (
    ("ADV-005", "ADV-006")
    in actual_relationships
)


# --------------------------------------------------
# Final result
# --------------------------------------------------

print("\n✓ Legitimate behavioral relationships reconstructed")
print("✓ Cross-device false correlations rejected")
print("✓ Long-range contextual correlations rejected")
print("✓ Same-user context did not create unsupported links")

print("\nTRACE v1.3 ADVERSARIAL SCENARIO PASSED")
print("=" * 65)