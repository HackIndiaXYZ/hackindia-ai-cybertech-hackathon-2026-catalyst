from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from evidence import build_evidence_record
from evidence_quality import build_evidence_quality
from clustering import build_incident_clusters
from incident import build_incident_analysis


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


# ------------------------------------------------------------
# 1. LOAD + NORMALIZE
# ------------------------------------------------------------

raw_events = load_events(scenario_file)
events = normalize_events(raw_events)


# ------------------------------------------------------------
# 2. CORRELATION
# ------------------------------------------------------------

relationships = build_sequence(events)


# ------------------------------------------------------------
# 3. EVIDENCE QUALITY
# ------------------------------------------------------------

evidence_relationships = build_evidence_quality(
    relationships
)


# ------------------------------------------------------------
# 4. INCIDENT CLUSTERING
# ------------------------------------------------------------

incidents = build_incident_clusters(
    events,
    relationships
)


# ------------------------------------------------------------
# 5. INCIDENT ANALYSIS
# ------------------------------------------------------------

analyses = [
    build_incident_analysis(
        incident,
        evidence_relationships
    )
    for incident in incidents
]


print()
print("TRACE v1.6 INTEGRATED PIPELINE")
print("=" * 70)

print(
    f"Raw events:          {len(raw_events)}"
)

print(
    f"Normalized events:   {len(events)}"
)

print(
    f"Relationships:       {len(relationships)}"
)

print(
    f"Incidents:            {len(incidents)}"
)


print()
print("INCIDENT ANALYSIS")
print("-" * 70)


for analysis in analyses:

    print(
        f"\n{analysis['incident_id']}"
    )

    print(
        f"Severity: {analysis['severity']}"
    )

    print(
        f"Risk score: {analysis['risk_score']}"
    )

    print(
        f"Events: {analysis['event_count']}"
    )

    print(
        f"Devices: {analysis['devices']}"
    )

    print(
        f"Users: {analysis['users']}"
    )

    print("\nRelationships:")

    for relationship in analysis[
        "relationships"
    ]:

        print(
            f"  {relationship['source']}"
            f" → "
            f"{relationship['target']}"
            f" | "
            f"{relationship['evidence_type']}"
            f" | "
            f"score={relationship['score']}"
        )


# ------------------------------------------------------------
# 6. EVIDENCE RECORD TEST
# ------------------------------------------------------------

assert len(relationships) > 0

evidence_record = build_evidence_record(
    relationships[0],
    events
)

assert "provenance" in evidence_record
assert "temporal_evidence" in evidence_record
assert "evidence" in evidence_record

assert (
    evidence_record["provenance"]["engine"]
    == "TRACE v1.6"
)

assert (
    evidence_record["temporal_evidence"]["ordered"]
    is True
)


# ------------------------------------------------------------
# 7. INCIDENT TESTS
# ------------------------------------------------------------

assert len(incidents) > 0

for analysis in analyses:

    assert "incident_id" in analysis
    assert "severity" in analysis
    assert "risk_score" in analysis
    assert "relationships" in analysis

    assert 0.0 <= analysis["risk_score"] <= 1.0


print()
print("✓ Correlation integrated")
print("✓ Evidence quality integrated")
print("✓ Incident clustering integrated")
print("✓ Incident scoring integrated")
print("✓ Evidence provenance verified")
print("✓ Temporal evidence verified")

print()
print("TRACE v1.6 INTEGRATED PIPELINE PASSED")
print("=" * 70)