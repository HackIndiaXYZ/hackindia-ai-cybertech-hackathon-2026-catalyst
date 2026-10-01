from datetime import datetime


WEIGHTS = {
    "same_user": 0.10,
    "same_device": 0.10,
    "same_ip": 0.05,
    "time_proximity": 0.10,
    "same_process": 0.15,
    "valid_sequence": 0.40,
    "resource_continuity": 0.10
}


# Valid event transitions TRACE can reconstruct.
ALLOWED_TRANSITIONS = {
    # Scenario 02: credential abuse
    "LOGIN_FAILED": {
        "LOGIN"
    },

    # Normal authentication flow
    "LOGIN": {
        "PROCESS_START"
    },

    # Process-driven activity
    "PROCESS_START": {
        "FILE_ACCESS",
        "NETWORK_CONNECTION",
        "PRIVILEGE_CHANGE"
    },

    # Privilege escalation / account abuse
    "PRIVILEGE_CHANGE": {
        "FILE_ACCESS"
    },

    # File access followed by network activity
    "FILE_ACCESS": {
        "NETWORK_CONNECTION"
    },

    # Network activity followed by transfer
    "NETWORK_CONNECTION": {
        "DATA_TRANSFER"
    }
}


# Events that should not create relationships.
IGNORED_EVENTS = {
    "HEARTBEAT"
}


def parse_time(timestamp):
    return datetime.fromisoformat(timestamp)


def same_context(event_a, event_b):
    """
    Determines whether two events share meaningful context.
    """

    same_device = (
        event_a.get("device")
        and
        event_a.get("device")
        == event_b.get("device")
    )

    same_user = (
        event_a.get("user")
        and
        event_a.get("user")
        == event_b.get("user")
    )

    same_process = (
        event_a.get("process")
        and
        event_b.get("process")
        and
        event_a.get("process")
        == event_b.get("process")
    )

    return (
        same_device
        or
        same_user
        or
        same_process
    )


def sequence_compatible(event_a, event_b):
    """
    Checks whether event_b is a valid successor of event_a.
    """

    event_type_a = event_a.get("event_type")
    event_type_b = event_b.get("event_type")

    allowed_next_events = ALLOWED_TRANSITIONS.get(
        event_type_a,
        set()
    )

    if event_type_b not in allowed_next_events:
        return False

    # If both events have devices, require the same device.
    device_a = event_a.get("device")
    device_b = event_b.get("device")

    if device_a and device_b:
        if device_a != device_b:
            return False

    return True


def compare_events(event_a, event_b):
    """
    Compare two events and return an explainable relationship
    when the relationship is valid.
    """

    # Ignore telemetry noise.
    if (
        event_a.get("event_type")
        in IGNORED_EVENTS
        or
        event_b.get("event_type")
        in IGNORED_EVENTS
    ):
        return None

    time_a = parse_time(
        event_a["timestamp"]
    )

    time_b = parse_time(
        event_b["timestamp"]
    )

    # Relationships must move forward in time.
    if time_b <= time_a:
        return None

    difference = (
        time_b - time_a
    ).total_seconds()

    # Do not correlate events that are too far apart.
    if difference > 300:
        return None

    # Require a known event transition.
    if not sequence_compatible(
        event_a,
        event_b
    ):
        return None

    score = 0.0
    reasons = []

    # Same user
    if (
        event_a.get("user")
        and
        event_a.get("user")
        ==
        event_b.get("user")
    ):
        score += WEIGHTS["same_user"]

        reasons.append(
            f"Same user: {event_a['user']}"
        )

    # Same device
    if (
        event_a.get("device")
        and
        event_a.get("device")
        ==
        event_b.get("device")
    ):
        score += WEIGHTS["same_device"]

        reasons.append(
            f"Same device: {event_a['device']}"
        )

    # Same IP
    if (
        event_a.get("ip")
        and
        event_a.get("ip")
        ==
        event_b.get("ip")
    ):
        score += WEIGHTS["same_ip"]

        reasons.append(
            f"Same IP: {event_a['ip']}"
        )

    # Temporal proximity
    score += WEIGHTS["time_proximity"]

    reasons.append(
        f"Events are {int(difference)} seconds apart"
    )

    # Same process
    if (
        event_a.get("process")
        and
        event_b.get("process")
        and
        event_a.get("process")
        ==
        event_b.get("process")
    ):
        score += WEIGHTS["same_process"]

        reasons.append(
            f"Same process: {event_a['process']}"
        )

    # Valid event sequence
    score += WEIGHTS["valid_sequence"]

    reasons.append(
        "Valid sequence: "
        f"{event_a['event_type']} → "
        f"{event_b['event_type']}"
    )

    # Same resource
    if (
        event_a.get("resource")
        and
        event_b.get("resource")
        and
        event_a.get("resource")
        ==
        event_b.get("resource")
    ):
        score += WEIGHTS["resource_continuity"]

        reasons.append(
            f"Same resource: {event_a['resource']}"
        )

    return {
        "event_a": event_a["event_id"],
        "event_b": event_b["event_id"],

        "event_type_a": event_a["event_type"],
        "event_type_b": event_b["event_type"],

        "score": round(
            score,
            2
        ),

        "reasons": reasons
    }


def has_intervening_valid_predecessor(
    events,
    start_index,
    candidate_index
):
    """
    Prevents TRACE from skipping a stronger intermediate event.

    Example:

        LOGIN
          ↓
        PROCESS_START
          ↓
        FILE_ACCESS

    TRACE should not create:

        LOGIN → FILE_ACCESS

    when PROCESS_START already provides the valid intermediate
    sequence.
    """

    candidate_event = events[
        candidate_index
    ]

    candidate_type = candidate_event[
        "event_type"
    ]

    for index in range(
        start_index + 1,
        candidate_index
    ):

        intermediate = events[
            index
        ]

        if (
            intermediate.get("event_type")
            in IGNORED_EVENTS
        ):
            continue

        intermediate_type = intermediate.get(
            "event_type"
        )

        valid_predecessor = (
            candidate_type
            in ALLOWED_TRANSITIONS.get(
                intermediate_type,
                set()
            )
        )

        if not valid_predecessor:
            continue

        if same_context(
            intermediate,
            candidate_event
        ):
            return True

    return False


def build_sequence(events):
    """
    Build the strongest explainable sequence of
    relationships between normalized events.
    """

    # Always process chronologically.
    events = sorted(
        events,
        key=lambda event:
        parse_time(
            event["timestamp"]
        )
    )

    relationships = []

    for i in range(
        len(events) - 1
    ):

        current_event = events[
            i
        ]

        # Skip telemetry noise.
        if (
            current_event.get("event_type")
            in IGNORED_EVENTS
        ):
            continue

        candidates = []

        for j in range(
            i + 1,
            len(events)
        ):

            candidate_event = events[
                j
            ]

            # Skip telemetry noise.
            if (
                candidate_event.get("event_type")
                in IGNORED_EVENTS
            ):
                continue

            relationship = compare_events(
                current_event,
                candidate_event
            )

            if not relationship:
                continue

            # Avoid jumping over a stronger intermediate event.
            if has_intervening_valid_predecessor(
                events,
                i,
                j
            ):
                continue

            candidates.append(
                relationship
            )

        if not candidates:
            continue

        # Keep strongest valid successor.
        strongest = max(
            candidates,
            key=lambda relationship:
            relationship["score"]
        )

        relationships.append(
            strongest
        )

    return relationships