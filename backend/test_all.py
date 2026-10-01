import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent


TESTS = [
    ("v1.1 Temporal Sequence", "test_temporal_sequence.py"),
    ("v1.2 Benign Scenario", "test_scenario_02.py"),
    ("v1.3 Adversarial Scenario", "test_scenario_03.py"),
    ("v1.4 Out-of-Order Telemetry", "test_scenario_04.py"),
]


def run_test(name, filename):
    print()
    print("=" * 70)
    print(f"RUNNING: {name}")
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(BACKEND_DIR / filename)
        ],
        cwd=BACKEND_DIR.parent
    )

    return result.returncode == 0


def main():
    print()
    print("TRACE REGRESSION SUITE")
    print("=" * 70)

    results = []

    for name, filename in TESTS:
        passed = run_test(name, filename)
        results.append((name, passed))

    print()
    print("=" * 70)
    print("TRACE REGRESSION SUMMARY")
    print("=" * 70)

    passed_count = 0

    for name, passed in results:
        status = "PASS" if passed else "FAIL"

        print(
            f"[{status}] {name}"
        )

        if passed:
            passed_count += 1

    print()
    print(
        f"{passed_count} / {len(results)} TESTS PASSED"
    )

    if passed_count == len(results):
        print()
        print("TRACE REGRESSION SUITE PASSED")
        print("=" * 70)
        sys.exit(0)

    print()
    print("TRACE REGRESSION SUITE FAILED")
    print("=" * 70)
    sys.exit(1)


if __name__ == "__main__":
    main()