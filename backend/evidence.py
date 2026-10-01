from datetime import datetime


ENGINE_VERSION = "TRACE v1.6"


def build_evidence_record(relationship, events):
    """
    Build a provenance-preserving evidence record
    for a reconstructed relationship.
    """

    event_map = {
        event["event_id"]: event
        for event in events
    }

    event_a = event_map[relationship["event_a"]]
    event_b = event_map[relationship["event_b"]]

    timestamp_a = datetime.fromisoformat(
        event_a["timestamp"]
    )

    timestamp_b = datetime.fromisoformat(
        event_b["timestamp"]
    )

    time_delta = (
        timestamp_b - timestamp_a
    ).total_seconds()

    return {
        "relationship": (
            f"{relationship['event_a']} → "
            f"{relationship['event_b']}"
        ),

        "confidence": relationship["score"],

        "event_a": {
            "event_id": event_a["event_id"],
            "timestamp": event_a["timestamp"],
            "event_type": event_a["event_type"],
            "source": event_a["source"],
            "user": event_a["user"],
            "device": event_a["device"],
            "process": event_a["process"],
            "resource": event_a["resource"]
        },

        "event_b": {
            "event_id": event_b["event_id"],
            "timestamp": event_b["timestamp"],
            "event_type": event_b["event_type"],
            "source": event_b["source"],
            "user": event_b["user"],
            "device": event_b["device"],
            "process": event_b["process"],
            "resource": event_b["resource"]
        },

        "temporal_evidence": {
            "delta_seconds": int(time_delta),
            "ordered": timestamp_b > timestamp_a
        },

        "evidence": relationship["reasons"],

        "provenance": {
            "engine": ENGINE_VERSION,
            "method": "sequence-aware correlation",
            "source_events": [
                event_a["event_id"],
                event_b["event_id"]
            ]
        }
    }