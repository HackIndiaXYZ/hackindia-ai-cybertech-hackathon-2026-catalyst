from datetime import datetime


ENGINE_VERSION = "TRACE v1.7"


def build_timeline(incident, events):
    """
    Build a chronological timeline for an incident.
    """

    incident_event_ids = set(
        incident["events"]
    )

    timeline = [
        event
        for event in events
        if event["event_id"] in incident_event_ids
    ]

    timeline.sort(
        key=lambda event:
        datetime.fromisoformat(event["timestamp"])
    )

    return [
        {
            "event_id": event["event_id"],
            "timestamp": event["timestamp"],
            "event_type": event["event_type"],
            "source": event["source"],
            "user": event["user"],
            "device": event["device"],
            "process": event["process"],
            "resource": event["resource"]
        }
        for event in timeline
    ]


def build_investigation_report(
    events,
    relationships,
    evidence_relationships,
    incidents,
    analyses
):
    """
    Build the unified TRACE investigation report.

    This function creates the stable output contract
    that the future API and frontend will consume.
    """

    incident_reports = []

    analysis_map = {
        analysis["incident_id"]: analysis
        for analysis in analyses
    }

    for incident in incidents:

        analysis = analysis_map[
            incident["incident_id"]
        ]

        incident_event_ids = set(
            incident["events"]
        )

        evidence = []

        for relationship in evidence_relationships:

            if (
                relationship["event_a"]
                not in incident_event_ids
                or
                relationship["event_b"]
                not in incident_event_ids
            ):
                continue

            evidence.append({
                "source": relationship["event_a"],
                "target": relationship["event_b"],
                "event_type": (
                    f"{relationship['event_type_a']}"
                    f" → "
                    f"{relationship['event_type_b']}"
                ),
                "correlation_score": relationship["score"],
                "evidence_type": (
                    relationship["evidence_type"]
                ),
                "evidence_weight": (
                    relationship["evidence_weight"]
                ),
                "reasons": relationship["reasons"]
            })

        incident_reports.append({
            "incident_id": incident["incident_id"],
            "severity": analysis["severity"],
            "risk_score": analysis["risk_score"],
            "event_count": incident["event_count"],
            "users": incident["users"],
            "devices": incident["devices"],
            "event_types": incident["event_types"],
            "timeline": build_timeline(
                incident,
                events
            ),
            "relationships": evidence,
            "indicators": analysis["indicators"]
        })

    incident_reports.sort(
        key=lambda incident:
        incident["risk_score"],
        reverse=True
    )

    return {
        "trace": {
            "engine": ENGINE_VERSION,
            "method": "sequence-aware correlation",
            "report_type": "incident_investigation"
        },

        "summary": {
            "total_events": len(events),
            "reconstructed_relationships": (
                len(relationships)
            ),
            "incident_count": len(incidents),
            "high_severity_incidents": sum(
                1
                for incident in incident_reports
                if incident["severity"] == "HIGH"
            )
        },

        "incidents": incident_reports
    }