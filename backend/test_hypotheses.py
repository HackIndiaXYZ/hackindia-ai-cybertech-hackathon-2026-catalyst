"""
TRACE v1.11
Hypothesis Engine Regression Test

Validates that the hypothesis engine:
1. Generates reports for reconstructed incidents.
2. Generates H1 for the suspicious data-transfer incident.
3. Generates H2 for a legitimate login/process incident.
4. Keeps evidence structures valid.
5. Produces deterministic, bounded evidence scores.
"""

import json
from pathlib import Path

from normalizer import normalize_events
from correlation import build_sequence
from evidence_quality import build_evidence_quality
from clustering import build_incident_clusters
from hypotheses import build_hypothesis_report


BASE_DIR = Path(__file__).resolve().parent.parent

SCENARIO_FILE = (
    BASE_DIR
    / "data"
    / "scenarios"
    / "scenario_01.json"
)


def load_scenario():
    with open(
        SCENARIO_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def find_hypothesis(
    hypotheses,
    hypothesis_id
):
    return next(
        (
            hypothesis
            for hypothesis in hypotheses
            if hypothesis["id"] == hypothesis_id
        ),
        None
    )


def test_hypothesis_engine():

    # =========================================================
    # 1. Load scenario
    # =========================================================

    raw_events = load_scenario()

    assert raw_events, (
        "Scenario contains no events"
    )

    # =========================================================
    # 2. Run TRACE pipeline
    # =========================================================

    events = normalize_events(
        raw_events
    )

    assert events, (
        "Normalization produced no events"
    )

    relationships = build_sequence(
        events
    )

    assert relationships, (
        "Correlation produced no relationships"
    )

    evidence_relationships = (
        build_evidence_quality(
            relationships
        )
    )

    assert evidence_relationships, (
        "Evidence enrichment produced no relationships"
    )

    incidents = build_incident_clusters(
        events,
        relationships
    )

    assert incidents, (
        "No incident clusters generated"
    )

    # =========================================================
    # 3. Generate hypothesis reports
    # =========================================================

    reports = build_hypothesis_report(
        incidents,
        evidence_relationships
    )

    assert reports, (
        "No hypothesis reports generated"
    )

    assert len(reports) == len(
        incidents
    ), (
        "Every incident must have "
        "one hypothesis report"
    )

    # =========================================================
    # 4. Validate report structure
    # =========================================================

    report_map = {
        report["incident_id"]: report
        for report in reports
    }

    for incident in incidents:

        incident_id = incident[
            "incident_id"
        ]

        assert incident_id in report_map, (
            f"Missing hypothesis report "
            f"for {incident_id}"
        )

        report = report_map[
            incident_id
        ]

        assert report["engine"] == (
            "TRACE v1.11"
        ), (
            f"Incorrect hypothesis engine "
            f"version for {incident_id}"
        )

        assert isinstance(
            report["hypotheses"],
            list
        ), (
            f"Hypotheses must be a list "
            f"for {incident_id}"
        )

    # =========================================================
    # 5. Find suspicious incident
    # =========================================================

    suspicious_incident = next(
        (
            incident
            for incident in incidents
            if (
                "EVT-005"
                in incident["events"]
                and
                "EVT-007"
                in incident["events"]
                and
                "EVT-009"
                in incident["events"]
            )
        ),
        None
    )

    assert suspicious_incident is not None, (
        "Suspicious transfer incident "
        "was not reconstructed"
    )

    suspicious_report = report_map[
        suspicious_incident["incident_id"]
    ]

    suspicious_hypotheses = (
        suspicious_report["hypotheses"]
    )

    # =========================================================
    # 6. H1 must exist for suspicious incident
    # =========================================================

    h1 = find_hypothesis(
        suspicious_hypotheses,
        "H1"
    )

    assert h1 is not None, (
        "H1 suspicious-transfer hypothesis "
        "missing from suspicious incident"
    )

    assert (
        h1["title"]
        ==
        "Suspicious data access "
        "followed by external transfer"
    ), (
        "H1 title is incorrect"
    )

    assert h1["score"] > 0.0, (
        "H1 must have positive evidence score"
    )

    assert h1["score"] <= 1.0, (
        "H1 score exceeds maximum"
    )

    assert h1[
        "supporting_evidence"
    ], (
        "H1 must contain supporting evidence"
    )

    # =========================================================
    # 7. Validate H1 evidence
    # =========================================================

    h1_relationships = {
        item["relationship"]
        for item
        in h1["supporting_evidence"]
    }

    assert (
        "EVT-005 → EVT-007"
        in h1_relationships
    ), (
        "H1 missing FILE_ACCESS → "
        "NETWORK_CONNECTION evidence"
    )

    assert (
        "EVT-007 → EVT-009"
        in h1_relationships
    ), (
        "H1 missing NETWORK_CONNECTION → "
        "DATA_TRANSFER evidence"
    )

    # =========================================================
    # 8. Find legitimate login/process incident
    # =========================================================

    legitimate_incident = next(
        (
            incident
            for incident in incidents
            if (
                "EVT-001"
                in incident["events"]
                and
                "EVT-002"
                in incident["events"]
            )
        ),
        None
    )

    assert legitimate_incident is not None, (
        "Expected login/process incident "
        "was not reconstructed"
    )

    legitimate_report = report_map[
        legitimate_incident["incident_id"]
    ]

    legitimate_hypotheses = (
        legitimate_report["hypotheses"]
    )

    # =========================================================
    # 9. H2 must exist for legitimate activity
    # =========================================================

    h2 = find_hypothesis(
        legitimate_hypotheses,
        "H2"
    )

    assert h2 is not None, (
        "H2 legitimate-activity hypothesis "
        "missing from login/process incident"
    )

    assert h2["score"] > 0.0, (
        "H2 must have positive evidence score"
    )

    assert h2["score"] <= 1.0, (
        "H2 score exceeds maximum"
    )

    assert h2[
        "supporting_evidence"
    ], (
        "H2 must contain supporting evidence"
    )

    # =========================================================
    # 10. Validate every generated hypothesis
    # =========================================================

    total_hypotheses = 0

    for report in reports:

        for hypothesis in report[
            "hypotheses"
        ]:

            total_hypotheses += 1

            assert hypothesis.get(
                "id"
            ), (
                "Hypothesis ID missing"
            )

            assert hypothesis.get(
                "title"
            ), (
                "Hypothesis title missing"
            )

            score = hypothesis.get(
                "score"
            )

            assert isinstance(
                score,
                (int, float)
            ), (
                "Hypothesis score must "
                "be numeric"
            )

            assert 0.0 <= score <= 1.0, (
                f"Invalid hypothesis score: "
                f"{score}"
            )

            assert isinstance(
                hypothesis[
                    "supporting_evidence"
                ],
                list
            )

            assert isinstance(
                hypothesis[
                    "contradicting_evidence"
                ],
                list
            )

            assert isinstance(
                hypothesis[
                    "missing_evidence"
                ],
                list
            )

    assert total_hypotheses >= 2, (
        "Expected at least two hypotheses "
        "across scenario 01"
    )

    # =========================================================
    # 11. Validate competing evidence
    # =========================================================

    assert h1["score"] > h2["score"], (
        "Suspicious transfer hypothesis "
        "should have stronger reconstructed "
        "evidence than legitimate activity "
        "in this scenario"
    )

    # =========================================================
    # 12. Output validation summary
    # =========================================================

    print(
        "✓ Scenario loaded"
    )

    print(
        f"✓ {len(events)} events normalized"
    )

    print(
        f"✓ {len(relationships)} relationships reconstructed"
    )

    print(
        f"✓ {len(incidents)} incidents clustered"
    )

    print(
        f"✓ {total_hypotheses} hypotheses generated"
    )

    print(
        f"✓ H1 score: {h1['score']}"
    )

    print(
        f"✓ H2 score: {h2['score']}"
    )

    print(
        "✓ H1 supporting evidence validated"
    )

    print(
        "✓ H2 supporting evidence validated"
    )

    print(
        "✓ Hypothesis evidence structures valid"
    )

    print(
        "✓ Hypothesis scores within [0, 1]"
    )

    print(
        "✓ Competing hypothesis ordering valid"
    )

    print(
        "\nTRACE HYPOTHESIS TEST PASSED"
    )


if __name__ == "__main__":
    test_hypothesis_engine()