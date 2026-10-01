import json
from pathlib import Path


def load_events(file_path):
    """Load raw security events from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_event(event):
    """Convert an event into TRACE's common format."""
    return {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "event_type": event.get("event_type"),
        "user": event.get("user"),
        "device": event.get("device"),
        "ip": event.get("ip"),
        "process": event.get("process"),
        "resource": event.get("resource"),
        "source": event.get("source"),
        "raw_event": event
    }


def normalize_events(events):
    """Normalize all events."""
    return [normalize_event(event) for event in events]


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    scenario_file = project_root / "data" / "scenarios" / "scenario_01.json"

    raw_events = load_events(scenario_file)
    normalized_events = normalize_events(raw_events)

    print(f"Loaded events: {len(raw_events)}")
    print(f"Normalized events: {len(normalized_events)}")

    print("\nFirst normalized event:")
    print(normalized_events[0])