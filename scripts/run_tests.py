#!/usr/bin/env python3
"""
Automated Test Suite Runner & Orchestrator for Hotel Autonomous Revenue AI Agent.

Executes test suites across unit, api, forecasting, pricing, agent, security, and e2e modules.
Prints formatted execution logs, duration, pass/fail status, and coverage metrics.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

TEST_SUITES = {
    "unit": "backend/tests/unit",
    "api": "backend/tests/api",
    "forecasting": "backend/tests/forecasting",
    "pricing": "backend/tests/pricing",
    "agent": "backend/tests/agent",
    "security": "backend/tests/security",
    "e2e": "backend/tests/e2e",
}


def run_suite(suite_name: str, test_path: str, extra_args: list[str]) -> tuple[bool, str, float]:
    """
    Executes a single test suite using pytest.
    """
    full_path = ROOT_DIR / test_path
    if not full_path.exists():
        return False, f"Directory path {test_path} does not exist", 0.0

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(full_path),
        "-v",
        "--tb=short",
    ] + extra_args

    print(f"\n==================================================")
    print(f" Running Test Suite: [{suite_name.upper()}]")
    print(f" Target Path: {test_path}")
    print(f"==================================================")

    start_time = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)

    result = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env, capture_output=True, text=True)
    duration = time.time() - start_time

    success = (result.returncode == 0)
    output = result.stdout if success else f"{result.stdout}\n{result.stderr}"

    return success, output, duration


def main():
    parser = argparse.ArgumentParser(description="Hotel Revenue AI Agent Test Orchestrator")
    parser.add_argument(
        "--suite",
        choices=list(TEST_SUITES.keys()) + ["all"],
        default="all",
        help="Select specific test suite to run (default: all)",
    )
    parser.add_argument("--coverage", action="store_true", help="Generate code coverage report")
    args = parser.parse_args()

    extra_pytest_args = []
    if args.coverage:
        extra_pytest_args.extend(["--cov=backend/app", "--cov-report=term-missing"])

    suites_to_run = TEST_SUITES.keys() if args.suite == "all" else [args.suite]

    summary = []
    total_start = time.time()
    overall_success = True

    for s_name in suites_to_run:
        s_path = TEST_SUITES[s_name]
        success, log, duration = run_suite(s_name, s_path, extra_pytest_args)
        status = "PASSED" if success else "FAILED"
        if not success:
            overall_success = False

        summary.append({
            "suite": s_name,
            "status": status,
            "duration": f"{duration:.2f}s",
            "log": log,
        })
        print(log)

    total_duration = time.time() - total_start

    print("\n" + "=" * 65)
    print("                AUTOMATED TEST SUITE SUMMARY REPORT              ")
    print("=" * 65)
    print(f"{'Suite Name':<20} | {'Status':<12} | {'Duration':<12}")
    print("-" * 65)

    for item in summary:
        print(f"{item['suite']:<20} | {item['status']:<12} | {item['duration']:<12}")

    print("-" * 65)
    print(f"Total Execution Time: {total_duration:.2f} seconds")
    print(f"Overall Result: {'SUCCESS' if overall_success else 'FAILURE'}")
    print("=" * 65)

    if not overall_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
