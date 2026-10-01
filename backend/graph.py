import json
from pathlib import Path

from normalizer import load_events, normalize_events
from correlation import build_sequence
from evidence import build_evidence_record


def build_graph(events, relationships):
    """
    Convert reconstructed relationships into
    a machine-readable incident graph.
    """

    nodes = []
    edges = []

    # Create one graph node for every event.
    for event in events:
        nodes.append({
            "id": event["event_id"],
            "label": event["event_type"],
            "timestamp": event["timestamp"],
            "source": event["source"],
            "user": event["user"],
            "device": event["device"],
            "process": event["process"],
            "resource": event["resource"]
        })

    # Create graph edges from reconstructed relationships.
    for relationship in relationships:

        evidence_record = build_evidence_record(
            relationship,
            events
        )

        edges.append({
            "id": (
                f"{relationship['event_a']}"
                f"->{relationship['event_b']}"
            ),

            "source": relationship["event_a"],
            "target": relationship["event_b"],

            "relationship_type": "SEQUENCE",

            "relationship_score": relationship["score"],

            "evidence": evidence_record["evidence"],

            "provenance": evidence_record["provenance"]
        })

    return {
        "graph_version": "0.5",
        "nodes": nodes,
        "edges": edges
    }


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    scenario_file = (
        project_root
        / "data"
        / "scenarios"
        / "scenario_01.json"
    )

    output_file = (
        project_root
        / "data"
        / "scenario_01_graph.json"
    )

    # Load and normalize events.
    raw_events = load_events(scenario_file)
    events = normalize_events(raw_events)

    # Reconstruct sequence.
    relationships = build_sequence(events)

    # Build graph.
    graph = build_graph(
        events,
        relationships
    )

    # Save graph.
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            graph,
            file,
            indent=2
        )

    print("\nTRACE v0.5 INCIDENT GRAPH")
    print("=" * 50)

    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")

    print("\nGRAPH EDGES")
    print("-" * 50)

    for edge in graph["edges"]:

        print(
            f"{edge['source']} "
            f"→ "
            f"{edge['target']} "
            f"| score: "
            f"{edge['relationship_score']}"
        )

    print("\nGraph saved to:")
    print(output_file)