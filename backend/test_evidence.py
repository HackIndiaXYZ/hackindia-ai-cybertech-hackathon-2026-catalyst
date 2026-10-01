from normalizer import load_events, normalize_events
from correlation import build_sequence
from evidence import build_evidence_record

from pathlib import Path


project_root = Path(__file__).resolve().parent.parent

scenario_file = (
    project_root
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


raw_events = load_events(scenario_file)
events = normalize_events(raw_events)

relationships = build_sequence(events)


print("\nTRACE v0.4 EVIDENCE REPORT")
print("=" * 60)


for relationship in relationships:

    record = build_evidence_record(
        relationship,
        events
    )

    print("\nRELATIONSHIP")
    print("-" * 60)

    print(record["relationship"])
    print(f"Confidence: {record['confidence']}")

    print("\nEvidence:")

    for evidence in record["evidence"]:
        print(f"  ✓ {evidence}")

    print("\nProvenance:")
    print(f"  Engine: {record['provenance']['engine']}")
    print(f"  Method: {record['provenance']['method']}")
    print(
        f"  Source events: "
        f"{record['provenance']['source_events']}"
    )