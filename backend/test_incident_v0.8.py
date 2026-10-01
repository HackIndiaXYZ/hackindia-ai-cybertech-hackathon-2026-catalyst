from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from clustering import build_incident_clusters
from incident import build_incident_analysis


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


print("\nTRACE v0.8 PER-INCIDENT ANALYSIS")
print("=" * 65)


analyses = []

for incident in incidents:

    analysis = build_incident_analysis(
        incident,
        events,
        relationships
    )

    analyses.append(
        analysis
    )

    print("\n" + "-" * 65)

    print(
        f"Incident: "
        f"{analysis['incident_id']}"
    )

    print(
        f"Severity: "
        f"{analysis['severity']}"
    )

    print(
        f"Risk score: "
        f"{analysis['risk_score']}"
    )

    print(
        f"Events: "
        f"{analysis['event_count']}"
    )

    print(
        f"Devices: "
        f"{analysis['devices']}"
    )

    print("\nIndicators:")

    if analysis["indicators"]:

        for indicator in analysis["indicators"]:

            print(
                f"  ✓ {indicator}"
            )

    else:

        print(
            "  No strong behavioral indicators"
        )


# -------------------------
# Validation
# -------------------------

assert len(analyses) == len(
    incidents
)

for analysis in analyses:

    assert 0 <= analysis[
        "risk_score"
    ] <= 1

    assert analysis[
        "severity"
    ] in {
        "INFO",
        "LOW",
        "MEDIUM",
        "HIGH"
    }


# The Laptop-17 incident should contain
# the multi-stage behavior.
laptop17 = next(
    analysis
    for analysis in analyses
    if "LAPTOP-17"
    in analysis["devices"]
)

# The Laptop-22 activity should remain
# lower because it lacks the stronger
# multi-stage indicators.
laptop22 = next(
    analysis
    for analysis in analyses
    if "LAPTOP-22"
    in analysis["devices"]
)


assert laptop17["risk_score"] > laptop22[
    "risk_score"
]

print("\n✓ Each incident scored independently")
print("✓ Risk scores are within valid range")
print("✓ Multi-stage activity scores above simple activity")

print("\nTRACE v0.8 TEST PASSED")
print("=" * 65)