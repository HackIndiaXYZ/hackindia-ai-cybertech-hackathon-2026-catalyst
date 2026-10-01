EVIDENCE_WEIGHTS = {
    "CONTEXT": 0.10,
    "SEQUENCE": 0.25,
    "BEHAVIORAL": 0.50,
    "HIGH_VALUE": 0.75,
    "NOISE": 0.00
}


def classify_relationship(relationship):
    """
    Classify a relationship according to
    the strength of evidence it represents.
    """

    event_a = relationship["event_type_a"]
    event_b = relationship["event_type_b"]

    # High-value behavioral relationship
    if (
        event_a == "NETWORK_CONNECTION"
        and event_b == "DATA_TRANSFER"
    ):
        return "HIGH_VALUE"

    # Strong behavioral relationship
    if (
        event_a == "FILE_ACCESS"
        and event_b == "NETWORK_CONNECTION"
    ):
        return "BEHAVIORAL"

    if (
        event_a == "FILE_ACCESS"
        and event_b == "DATA_TRANSFER"
    ):
        return "BEHAVIORAL"

    # Normal expected sequence
    if (
        event_a == "LOGIN"
        and event_b == "PROCESS_START"
    ):
        return "SEQUENCE"

    if (
        event_a == "PROCESS_START"
        and event_b == "FILE_ACCESS"
    ):
        return "SEQUENCE"

    # Everything else is contextual
    return "CONTEXT"


def build_evidence_quality(relationships):
    """
    Add evidence classification and weight
    to every reconstructed relationship.
    """

    enriched = []

    for relationship in relationships:

        evidence_type = classify_relationship(
            relationship
        )

        evidence_weight = EVIDENCE_WEIGHTS[
            evidence_type
        ]

        enriched_relationship = {
            **relationship,

            "evidence_type": evidence_type,

            "evidence_weight": evidence_weight
        }

        enriched.append(
            enriched_relationship
        )

    return enriched