from pathlib import Path

from normalizer import (
    load_events,
    normalize_events
)

from correlation import (
    build_sequence
)


project_root = (
    Path(__file__).resolve().parent.parent
)


scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


# ---------------------------------------------
# Load scenario
# ---------------------------------------------

raw_events = load_events(
    scenario_file
)

events = normalize_events(
    raw_events
)


# ---------------------------------------------
# Reconstruct sequence
# ---------------------------------------------

relationships = build_sequence(
    events
)


print(
    "\nTRACE v1.1 TEMPORAL SEQUENCE"
)

print(
    "=" * 65
)


for relationship in relationships:

    print(
        f"{relationship['event_a']}"
        f" → "
        f"{relationship['event_b']}"
        f" | "
        f"{relationship['event_type_a']}"
        f" → "
        f"{relationship['event_type_b']}"
        f" | score: "
        f"{relationship['score']}"
    )


# ---------------------------------------------
# Expected valid relationships
# ---------------------------------------------

expected_relationships = {
    (
        "EVT-001",
        "EVT-002"
    ),

    (
        "EVT-004",
        "EVT-005"
    ),

    (
        "EVT-005",
        "EVT-007"
    ),

    (
        "EVT-006",
        "EVT-010"
    ),

    (
        "EVT-007",
        "EVT-009"
    )
}


actual_relationships = {
    (
        relationship["event_a"],
        relationship["event_b"]
    )
    for relationship in relationships
}


# ---------------------------------------------
# Validate expected relationships
# ---------------------------------------------

for expected in expected_relationships:

    assert expected in actual_relationships, (
        f"Missing expected relationship: "
        f"{expected}"
    )


# ---------------------------------------------
# Validate rejected long jump
# ---------------------------------------------

assert (
    "EVT-002",
    "EVT-005"
) not in actual_relationships


# ---------------------------------------------
# Validate invalid PROCESS_START →
# PROCESS_START relationship is absent
# ---------------------------------------------

assert (
    "EVT-002",
    "EVT-004"
) not in actual_relationships


# ---------------------------------------------
# Validate heartbeat isolation
# ---------------------------------------------

heartbeat_relationships = [
    relationship
    for relationship in relationships
    if (
        relationship["event_a"]
        == "EVT-003"
        or
        relationship["event_b"]
        == "EVT-003"
        or
        relationship["event_a"]
        == "EVT-008"
        or
        relationship["event_b"]
        == "EVT-008"
    )
]


assert len(
    heartbeat_relationships
) == 0


# ---------------------------------------------
# Final validation
# ---------------------------------------------

print(
    "\n✓ Expected behavioral relationships reconstructed"
)

print(
    "✓ Unsupported PROCESS_START → PROCESS_START link rejected"
)

print(
    "✓ Long-jump EVT-002 → EVT-005 rejected"
)

print(
    "✓ HEARTBEAT events remain unconnected"
)

print(
    "\nTRACE v1.1 TEST PASSED"
)

print(
    "=" * 65
)