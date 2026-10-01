from pathlib import Path

from normalizer import (
    load_events,
    normalize_events
)

from correlation import (
    build_sequence
)

from evidence_quality import (
    build_evidence_quality
)

from clustering import (
    build_incident_clusters
)

from incident import (
    build_incident_analysis
)

from investigation import (
    build_investigation_report
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


# ============================================================
# 1. LOAD EVENTS
# ============================================================

raw_events = load_events(
    scenario_file
)

events = normalize_events(
    raw_events
)


# ============================================================
# 2. CORRELATION
# ============================================================

relationships = build_sequence(
    events
)


# ============================================================
# 3. EVIDENCE QUALITY
# ============================================================

evidence_relationships = (
    build_evidence_quality(
        relationships
    )
)


# ============================================================
# 4. INCIDENT CLUSTERING
# ============================================================

incidents = build_incident_clusters(
    events,
    relationships
)


# ============================================================
# 5. INCIDENT ANALYSIS
# ============================================================

analyses = [
    build_incident_analysis(
        incident,
        evidence_relationships
    )
    for incident in incidents
]


# ============================================================
# 6. BUILD INVESTIGATION REPORT
# ============================================================

report = build_investigation_report(
    events,
    relationships,
    evidence_relationships,
    incidents,
    analyses
)


# ============================================================
# 7. DISPLAY REPORT
# ============================================================

print()
print("TRACE v1.7 INVESTIGATION REPORT")
print("=" * 70)

print("\nTRACE ENGINE")
print("-" * 70)

print(
    f"Engine: {report['trace']['engine']}"
)

print(
    f"Method: {report['trace']['method']}"
)

print(
    f"Report type: {report['trace']['report_type']}"
)


print("\nSUMMARY")
print("-" * 70)

summary = report["summary"]

print(
    f"Total events: "
    f"{summary['total_events']}"
)

print(
    f"Reconstructed relationships: "
    f"{summary['reconstructed_relationships']}"
)

print(
    f"Incidents: "
    f"{summary['incident_count']}"
)

print(
    f"High severity incidents: "
    f"{summary['high_severity_incidents']}"
)


print("\nINCIDENTS")
print("-" * 70)


for incident in report["incidents"]:

    print(
        f"\n{incident['incident_id']}"
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
        f"Events: "
        f"{incident['event_count']}"
    )

    print(
        f"Users: "
        f"{incident['users']}"
    )

    print(
        f"Devices: "
        f"{incident['devices']}"
    )

    print("\nTimeline:")

    for event in incident["timeline"]:

        print(
            f"  {event['timestamp']} | "
            f"{event['event_id']} | "
            f"{event['event_type']}"
        )

    print("\nEvidence:")

    for evidence in incident[
        "relationships"
    ]:

        print(
            f"  {evidence['source']}"
            f" → "
            f"{evidence['target']}"
            f" | "
            f"{evidence['evidence_type']}"
            f" | "
            f"score={evidence['correlation_score']}"
        )


# ============================================================
# 8. VALIDATION
# ============================================================

assert (
    report["trace"]["engine"]
    == "TRACE v1.7"
)

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

assert (
    report["summary"]
    ["high_severity_incidents"]
    == 1
)


# Highest-risk incident should be INC-002.

assert (
    report["incidents"][0]["incident_id"]
    == "INC-002"
)

assert (
    report["incidents"][0]["severity"]
    == "HIGH"
)

assert (
    report["incidents"][0]["risk_score"]
    == 0.96
)


# Timeline must be chronological.

timeline = report[
    "incidents"
][0]["timeline"]

timestamps = [
    event["timestamp"]
    for event in timeline
]

assert timestamps == sorted(
    timestamps
)


# Evidence must exist.

assert len(
    report["incidents"][0]["relationships"]
) == 3


print()
print("✓ Unified investigation report created")
print("✓ Incident summaries included")
print("✓ Chronological timelines included")
print("✓ Evidence relationships included")
print("✓ Risk ordering verified")
print("✓ Report contract validated")

print()
print("TRACE v1.7 INVESTIGATION REPORT PASSED")
print("=" * 70)