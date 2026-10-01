from collections import defaultdict


def build_adjacency(relationships):
    """
    Build an undirected adjacency map from
    reconstructed relationships.
    """

    adjacency = defaultdict(set)

    for relationship in relationships:
        source = relationship["event_a"]
        target = relationship["event_b"]

        adjacency[source].add(target)
        adjacency[target].add(source)

    return adjacency


def find_connected_components(relationships):
    """
    Find groups of events connected by relationships.

    Each connected component represents a candidate
    incident/activity cluster.
    """

    adjacency = build_adjacency(
        relationships
    )

    visited = set()
    components = []

    for event_id in adjacency:

        if event_id in visited:
            continue

        component = set()
        stack = [event_id]

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.add(current)

            for neighbor in adjacency[current]:

                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(
            sorted(component)
        )

    return components


def build_incident_clusters(
    events,
    relationships
):
    """
    Convert connected graph components into
    structured incident candidates.
    """

    components = find_connected_components(
        relationships
    )

    event_map = {
        event["event_id"]: event
        for event in events
    }

    incidents = []

    for index, component in enumerate(
        components,
        start=1
    ):

        component_events = [
            event_map[event_id]
            for event_id in component
        ]

        incidents.append({
            "incident_id": f"INC-{index:03d}",
            "event_count": len(component),
            "events": component,
            "event_types": [
                event["event_type"]
                for event in component_events
            ],
            "devices": sorted({
                event["device"]
                for event in component_events
                if event.get("device")
            }),
            "users": sorted({
                event["user"]
                for event in component_events
                if event.get("user")
            })
        })

    return incidents