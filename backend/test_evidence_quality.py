from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from evidence_quality import build_evidence_quality


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

evidence = build_evidence_quality(
    relationships
)


print("\nTRACE v0.9 EVIDENCE QUALITY")
print("=" * 70)


for relationship in evidence:

    print(
        f"\n{relationship['event_a']}"
        f" → "
        f"{relationship['event_b']}"
    )

    print(
        f"Evidence type: "
        f"{relationship['evidence_type']}"
    )

    print(
        f"Evidence weight: "
        f"{relationship['evidence_weight']}"
    )

    print(
        f"Correlation score: "
        f"{relationship['score']}"
    )


# --------------------------------
# Validation
# --------------------------------

assert len(evidence) > 0


for relationship in evidence:

    assert relationship[
        "evidence_type"
    ] in {
        "CONTEXT",
        "SEQUENCE",
        "BEHAVIORAL",
        "HIGH_VALUE",
        "NOISE"
    }

    assert 0 <= relationship[
        "evidence_weight"
    ] <= 1


high_value = [
    relationship
    for relationship in evidence
    if relationship["evidence_type"]
    == "HIGH_VALUE"
]

behavioral = [
    relationship
    for relationship in evidence
    if relationship["evidence_type"]
    == "BEHAVIORAL"
]


assert len(high_value) > 0
assert len(behavioral) > 0

assert all(
    relationship["evidence_weight"]
    >= 0.75
    for relationship in high_value
)

assert all(
    relationship["evidence_weight"]
    >= 0.50
    for relationship in behavioral
)


print("\n✓ Every relationship has evidence quality")
print("✓ Behavioral evidence identified")
print("✓ High-value evidence identified")
print("✓ Evidence weights are bounded")
print("\nTRACE v0.9 TEST PASSED")
print("=" * 70)