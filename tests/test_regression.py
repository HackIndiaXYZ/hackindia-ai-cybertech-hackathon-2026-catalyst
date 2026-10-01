import sys
from pathlib import Path
import json

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend folder to Python path
BACKEND_DIR = BASE_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import backend modules
from normalizer import normalize_events
from correlation import build_sequence


SCENARIOS_DIR = BASE_DIR / "data" / "scenarios"


def run_scenario(number):
    scenario_file = SCENARIOS_DIR / f"scenario_{number:02d}.json"

    with open(scenario_file, "r", encoding="utf-8") as file:
        raw_events = json.load(file)

    events = normalize_events(raw_events)
    relationships = build_sequence(events)

    return events, relationships


def get_relationship_types(relationships):
    return {
        (
            relationship["event_type_a"],
            relationship["event_type_b"]
        )
        for relationship in relationships
    }


def test_temporal_sequence():
    events, relationships = run_scenario(1)

    assert events
    assert relationships

    relationship_types = get_relationship_types(relationships)

    assert ("LOGIN", "PROCESS_START") in relationship_types
    assert ("PROCESS_START", "FILE_ACCESS") in relationship_types
    assert ("FILE_ACCESS", "NETWORK_CONNECTION") in relationship_types
    assert ("NETWORK_CONNECTION", "DATA_TRANSFER") in relationship_types

    print("✓ Scenario 01 temporal sequence passed")


def test_benign_scenario():
    events, relationships = run_scenario(2)

    assert events

    relationship_types = get_relationship_types(relationships)

    assert ("FILE_ACCESS", "NETWORK_CONNECTION") not in relationship_types

    print("✓ Scenario 02 benign scenario passed")


def test_adversarial_scenario():
    events, relationships = run_scenario(3)

    assert events

    relationship_types = get_relationship_types(relationships)

    assert ("FILE_ACCESS", "NETWORK_CONNECTION") in relationship_types
    assert ("NETWORK_CONNECTION", "DATA_TRANSFER") in relationship_types

    print("✓ Scenario 03 adversarial scenario passed")


def test_out_of_order_telemetry():
    events, relationships = run_scenario(4)

    assert events

    for relationship in relationships:
        assert relationship["event_type_a"]
        assert relationship["event_type_b"]
        assert relationship["score"] >= 0.0

    print("✓ Scenario 04 out-of-order telemetry passed")


if __name__ == "__main__":
    print()
    print("TRACE REGRESSION TEST")
    print("=" * 55)

    test_temporal_sequence()
    test_benign_scenario()
    test_adversarial_scenario()
    test_out_of_order_telemetry()

    print()
    print("✓ TRACE REGRESSION TEST PASSED")