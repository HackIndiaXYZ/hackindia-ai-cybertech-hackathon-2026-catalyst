"""
TRACE v1.11
Competing Incident Hypothesis Engine

Generates deterministic, explainable hypotheses from
reconstructed evidence relationships.

No LLM dependency.
"""

ENGINE_VERSION = "TRACE v1.11"


def _relationship_matches(
    relationships,
    event_type_a,
    event_type_b
):
    """
    Return relationships matching a specific
    event-type transition.
    """
    return [
        relationship
        for relationship in relationships
        if (
            relationship.get("event_type_a")
            == event_type_a
            and
            relationship.get("event_type_b")
            == event_type_b
        )
    ]


def generate_hypotheses(
    incident,
    evidence_relationships
):
    """
    Generate competing explanations for one incident.

    Hypotheses are generated only from evidence
    reconstructed inside the current incident.

    The engine is deterministic:
    the same evidence produces the same hypotheses.
    """

    incident_event_ids = set(
        incident.get("events", [])
    )

    # Only relationships belonging to this incident.
    relationships = [
        relationship
        for relationship in evidence_relationships
        if (
            relationship.get("event_a")
            in incident_event_ids
            and
            relationship.get("event_b")
            in incident_event_ids
        )
    ]

    hypotheses = []

    # =========================================================
    # H1: Suspicious data access followed by external transfer
    # =========================================================

    file_to_network = _relationship_matches(
        relationships,
        "FILE_ACCESS",
        "NETWORK_CONNECTION"
    )

    network_to_transfer = _relationship_matches(
        relationships,
        "NETWORK_CONNECTION",
        "DATA_TRANSFER"
    )

    file_to_transfer = _relationship_matches(
        relationships,
        "FILE_ACCESS",
        "DATA_TRANSFER"
    )

    supporting = []

    for relationship in file_to_network:
        supporting.append({
            "relationship": (
                f"{relationship['event_a']} → "
                f"{relationship['event_b']}"
            ),
            "reason": (
                "File access was followed by "
                "an external network connection."
            ),
            "weight": relationship.get(
                "evidence_weight",
                0.0
            )
        })

    for relationship in network_to_transfer:
        supporting.append({
            "relationship": (
                f"{relationship['event_a']} → "
                f"{relationship['event_b']}"
            ),
            "reason": (
                "Network activity was followed "
                "by a data transfer."
            ),
            "weight": relationship.get(
                "evidence_weight",
                0.0
            )
        })

    for relationship in file_to_transfer:
        supporting.append({
            "relationship": (
                f"{relationship['event_a']} → "
                f"{relationship['event_b']}"
            ),
            "reason": (
                "File access is directly associated "
                "with a subsequent data transfer."
            ),
            "weight": relationship.get(
                "evidence_weight",
                0.0
            )
        })

    if supporting:

        missing = []

        event_types = {
            event_type
            for relationship in relationships
            for event_type in (
                relationship.get("event_type_a"),
                relationship.get("event_type_b")
            )
        }

        if "LOGIN" not in event_types:
            missing.append(
                "No authentication evidence in "
                "the reconstructed chain."
            )

        if "PROCESS_START" not in event_types:
            missing.append(
                "No process execution evidence "
                "supports the activity."
            )

        base_score = 0.55

        high_value_count = sum(
            1
            for item in supporting
            if item["weight"] >= 0.75
        )

        behavioral_count = sum(
            1
            for item in supporting
            if item["weight"] >= 0.50
        )

        score = (
            base_score
            + min(
                high_value_count * 0.12,
                0.24
            )
            + min(
                behavioral_count * 0.06,
                0.12
            )
        )

        score = min(
            round(score, 2),
            0.95
        )

        hypotheses.append({
            "id": "H1",
            "title": (
                "Suspicious data access "
                "followed by external transfer"
            ),
            "score": score,
            "supporting_evidence": supporting,
            "contradicting_evidence": [],
            "missing_evidence": missing
        })

    # =========================================================
    # H2: Legitimate administrative activity
    # =========================================================

    legitimate_support = []

    for relationship in relationships:

        if (
            relationship.get("event_type_a")
            == "LOGIN"
            and
            relationship.get("event_type_b")
            == "PROCESS_START"
        ):

            legitimate_support.append({
                "relationship": (
                    f"{relationship['event_a']} → "
                    f"{relationship['event_b']}"
                ),
                "reason": (
                    "Process activity follows an "
                    "observed authentication event."
                ),
                "weight": relationship.get(
                    "evidence_weight",
                    0.0
                )
            })

    if legitimate_support:

        score = 0.30

        score += min(
            len(legitimate_support) * 0.04,
            0.10
        )

        if network_to_transfer:
            score -= 0.06

        score = max(
            round(score, 2),
            0.05
        )

        hypotheses.append({
            "id": "H2",
            "title": (
                "Legitimate administrative activity"
            ),
            "score": score,
            "supporting_evidence": (
                legitimate_support
            ),
            "contradicting_evidence": (
                [{
                    "reason": (
                        "External transfer activity "
                        "is present in the same chain."
                    ),
                    "relationships": [
                        (
                            f"{relationship['event_a']} → "
                            f"{relationship['event_b']}"
                        )
                        for relationship
                        in network_to_transfer
                    ]
                }]
                if network_to_transfer
                else []
            ),
            "missing_evidence": [
                "No explicit administrative "
                "authorization evidence."
            ]
        })

    # =========================================================
    # H3: Generic process-driven file activity
    # =========================================================

    process_to_file = _relationship_matches(
        relationships,
        "PROCESS_START",
        "FILE_ACCESS"
    )

    if (
        process_to_file
        and
        not supporting
    ):

        hypotheses.append({
            "id": "H3",
            "title": (
                "Process-driven file activity"
            ),
            "score": 0.42,
            "supporting_evidence": [
                {
                    "relationship": (
                        f"{relationship['event_a']} → "
                        f"{relationship['event_b']}"
                    ),
                    "reason": (
                        "A process accessed a file "
                        "within the reconstructed sequence."
                    ),
                    "weight": relationship.get(
                        "evidence_weight",
                        0.0
                    )
                }
                for relationship
                in process_to_file
            ],
            "contradicting_evidence": [],
            "missing_evidence": [
                "No network transfer evidence "
                "was reconstructed."
            ]
        })

    # Strongest evidence first.
    hypotheses.sort(
        key=lambda hypothesis:
        hypothesis["score"],
        reverse=True
    )

    return hypotheses


def build_hypothesis_report(
    incidents,
    evidence_relationships
):
    """
    Build hypothesis analysis for every incident.

    Incidents without sufficient evidence may
    legitimately contain zero hypotheses.
    """

    reports = []

    for incident in incidents:

        hypotheses = generate_hypotheses(
            incident,
            evidence_relationships
        )

        reports.append({
            "incident_id": incident[
                "incident_id"
            ],
            "engine": ENGINE_VERSION,
            "hypotheses": hypotheses
        })

    return reports