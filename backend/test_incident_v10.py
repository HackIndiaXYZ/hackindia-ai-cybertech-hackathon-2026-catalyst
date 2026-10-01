from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from clustering import build_incident_clusters
from evidence_quality import build_evidence_quality
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

evidence_relationships = build_evidence_quality(
    relationships
)

incidents = build_incident_clusters(
    events,
    relationships
)


print("\nTRACE v1.0 EVIDENCE-WEIGHTED RISK")
print("=" * 70)


analyses = []

for incident in incidents:

    analysis = build_incident_analysis(
        incident,
        evidence_relationships
    )

    analyses.append(
        analysis
    )

    print("\n" + "-" * 70)

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

    print("\nEvidence:")

    for relationship in analysis[
        "relationships"
    ]:

        print(
            f"  {relationship['source']}"
            f" → "
            f"{relationship['target']}"
            f" | "
            f"{relationship['evidence_type']}"
            f" | weight: "
            f"{relationship['evidence_weight']}"
        )


# -------------------------
# Validation
# -------------------------

assert len(analyses) == 2

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


laptop17 = next(
    analysis
    for analysis in analyses
    if "LAPTOP-17"
    in analysis["devices"]
)

laptop22 = next(
    analysis
    for analysis in analyses
    if "LAPTOP-22"
    in analysis["devices"]
)


# The multi-stage incident must score higher.
assert laptop17["risk_score"] > laptop22[
    "risk_score"
]


# The score should no longer automatically
# saturate at 1.0 for this scenario.
assert laptop17["risk_score"] < 1.0


# Laptop-17 must contain high-value evidence.
assert any(
    relationship["evidence_type"]
    == "HIGH_VALUE"
    for relationship in laptop17[
        "relationships"
    ]
)


print("\n✓ Incidents scored independently")
print("✓ Evidence quality affects risk")
print("✓ High-value evidence detected")
print("✓ Multi-stage incident scores higher")
print("✓ Risk score does not automatically saturate")

print("\nTRACE v1.0 TEST PASSED")
print("=" * 70)