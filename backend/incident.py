def calculate_incident_score(
    incident,
    events,
    evidence_relationships
):
    """
    Calculate an evidence-weighted heuristic risk score
    for one incident.

    This is NOT a probability.
    """

    incident_event_ids = set(
        incident["events"]
    )

    incident_relationships = [
        relationship
        for relationship in evidence_relationships
        if (
            relationship["event_a"]
            in incident_event_ids
            and
            relationship["event_b"]
            in incident_event_ids
        )
    ]

    if not incident_relationships:
        return 0.0, [
            "No reconstructed relationships"
        ]

    # Use the strongest evidence rather than simply
    # adding every relationship together.
    evidence_scores = [
        relationship["evidence_weight"]
        for relationship in incident_relationships
    ]

    strongest = max(evidence_scores)

    # Additional independent evidence contributes,
    # but with diminishing influence.
    additional = sum(
        sorted(
            evidence_scores,
            reverse=True
        )[1:3]
    ) * 0.15

    # Multiple high-quality relationships indicate
    # a stronger reconstructed behavioral chain.
    high_quality_count = sum(
        1
        for relationship in incident_relationships
        if relationship["evidence_type"]
        in {
            "BEHAVIORAL",
            "HIGH_VALUE"
        }
    )

    chain_bonus = min(
        high_quality_count * 0.05,
        0.15
    )

    score = (
        strongest
        + additional
        + chain_bonus
    )

    score = min(
        round(score, 2),
        1.0
    )

    indicators = []

    for relationship in incident_relationships:

        if relationship["evidence_type"] == "HIGH_VALUE":

            indicators.append(
                "High-value behavioral evidence observed"
            )

        elif relationship["evidence_type"] == "BEHAVIORAL":

            indicators.append(
                "Behavioral evidence observed"
            )

    # Remove duplicates while preserving order.
    indicators = list(
        dict.fromkeys(indicators)
    )

    return score, indicators


def classify_incident(score):

    if score >= 0.75:
        return "HIGH"

    if score >= 0.45:
        return "MEDIUM"

    if score >= 0.20:
        return "LOW"

    return "INFO"


def build_incident_analysis(
    incident,
    evidence_relationships
):

    score, indicators = calculate_incident_score(
        incident,
        [],
        evidence_relationships
    )

    severity = classify_incident(score)

    incident_event_ids = set(
        incident["events"]
    )

    relationships = [
        {
            "source": relationship["event_a"],
            "target": relationship["event_b"],
            "score": relationship["score"],
            "evidence_type": relationship[
                "evidence_type"
            ],
            "evidence_weight": relationship[
                "evidence_weight"
            ]
        }
        for relationship in evidence_relationships
        if (
            relationship["event_a"]
            in incident_event_ids
            and
            relationship["event_b"]
            in incident_event_ids
        )
    ]

    return {
        "incident_id": incident["incident_id"],
        "severity": severity,
        "risk_score": score,
        "event_count": incident["event_count"],
        "events": incident["events"],
        "devices": incident["devices"],
        "users": incident["users"],
        "indicators": indicators,
        "relationships": relationships
    }