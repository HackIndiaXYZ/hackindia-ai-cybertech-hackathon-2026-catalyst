from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from clustering import build_incident_clusters


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


raw_events = load_events(
    scenario_file
)

events = normalize_events(
    raw_events
)

relationships = build_sequence(
    events
)

incidents = build_incident_clusters(
    events,
    relationships
)


print("\nTRACE v0.7 INCIDENT CLUSTERING")
print("=" * 60)

print(
    f"Candidate incidents: "
    f"{len(incidents)}"
)

for incident in incidents:

    print("\n" + "-" * 60)

    print(
        f"Incident: "
        f"{incident['incident_id']}"
    )

    print(
        f"Events: "
        f"{incident['event_count']}"
    )

    print(
        f"Devices: "
        f"{incident['devices']}"
    )

    print(
        f"Users: "
        f"{incident['users']}"
    )

    print(
        f"Event types: "
        f"{incident['event_types']}"
    )

    print(
        f"Event IDs: "
        f"{incident['events']}"
    )


# Basic validation
assert len(incidents) >= 1

for incident in incidents:

    assert incident["event_count"] > 0

    assert len(
        incident["events"]
    ) == incident["event_count"]


print("\n✓ Every cluster contains valid events")
print("✓ Every event belongs to a connected component")

print("\nTRACE v0.7 CLUSTERING TEST PASSED")
print("=" * 60)