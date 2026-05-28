"""
Regression Analyzer — Risk-based intelligent test selection.
Analyzes code change diffs and historical defect data to recommend
the minimal high-coverage test subset.
"""

import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
BACKLOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "work_items", "backlog.json")

# Map of changed file keywords → affected test modules
CHANGE_TO_MODULE_MAP = {
    "registration": ["tests/test_registration.py"],
    "registrationcontroller": ["tests/test_registration.py"],
    "usermodel": ["tests/test_registration.py"],
    "passwordvalidator": ["tests/test_registration.py"],
    "emailservice": ["tests/test_registration.py", "tests/test_forgot_password.py"],
    "forgotpassword": ["tests/test_forgot_password.py"],
    "passwordresetcontroller": ["tests/test_forgot_password.py"],
    "tokenservice": ["tests/test_forgot_password.py"],
    "portal": ["tests/test_registration.py", "tests/test_forgot_password.py"],
    "auth": ["tests/test_registration.py", "tests/test_forgot_password.py"],
}

RISK_SCORE_MAP = {
    "registrationcontroller": 0.85,
    "emailservice": 0.70,
    "usermodel": 0.40,
    "passwordvalidator": 0.55,
    "passwordresetcontroller": 0.55,
    "tokenservice": 0.65,
    "portal": 0.30,
    "auth": 0.75,
    "registration": 0.80,
    "forgotpassword": 0.50,
}


def analyze(changed_files: list) -> dict:
    """
    Analyze a list of changed files/components and return a risk-ranked
    list of test modules to execute.

    Args:
        changed_files: List of changed file names or component names

    Returns:
        dict with recommended tests, risk scores, and execution command
    """
    impacted_modules = {}

    for f in changed_files:
        key = f.lower().replace(".py", "").replace(".js", "").replace("_", "").replace("-", "")
        for pattern, modules in CHANGE_TO_MODULE_MAP.items():
            if pattern in key or key in pattern:
                risk = RISK_SCORE_MAP.get(pattern, 0.3)
                for mod in modules:
                    existing = impacted_modules.get(mod, 0)
                    impacted_modules[mod] = max(existing, risk)

    if not impacted_modules:
        return {
            "recommendation": "NO_DIRECT_IMPACT",
            "message": f"No direct test mappings found for: {changed_files}. "
                       "Run smoke tests as a precaution.",
            "tests": [],
            "command": "pytest qa_framework/tests/ -m smoke -v"
        }

    # Sort by risk score (highest first)
    sorted_modules = sorted(impacted_modules.items(), key=lambda x: x[1], reverse=True)

    high_risk = [(m, r) for m, r in sorted_modules if r >= 0.7]
    medium_risk = [(m, r) for m, r in sorted_modules if 0.4 <= r < 0.7]
    low_risk = [(m, r) for m, r in sorted_modules if r < 0.4]

    recommended_tests = [m for m, _ in high_risk + medium_risk]
    command_paths = [f"qa_framework/{m}" for m in recommended_tests]
    command = "pytest " + " ".join(command_paths) + " -v --html=qa_framework/reports/html/report.html"

    result = {
        "recommendation": "RISK_BASED_SELECTION",
        "changed_files": changed_files,
        "high_risk_tests": [{"module": m, "risk_score": round(r, 2)} for m, r in high_risk],
        "medium_risk_tests": [{"module": m, "risk_score": round(r, 2)} for m, r in medium_risk],
        "low_risk_tests": [{"module": m, "risk_score": round(r, 2)} for m, r in low_risk],
        "recommended_command": command,
        "total_impacted": len(impacted_modules),
        "deferred": [m for m, _ in low_risk]
    }

    print(f"\n{'='*60}")
    print(f"  🔬 Regression Analyzer Report")
    print(f"  Changed Files: {', '.join(changed_files)}")
    print(f"{'='*60}")
    print(f"\n  🔴 HIGH RISK — Run Immediately ({len(high_risk)} suites):")
    for m, r in high_risk:
        print(f"     [{r:.2f}] {m}")
    print(f"\n  🟡 MEDIUM RISK — Run Before Release ({len(medium_risk)} suites):")
    for m, r in medium_risk:
        print(f"     [{r:.2f}] {m}")
    print(f"\n  🟢 LOW RISK — Defer to Nightly ({len(low_risk)} suites):")
    for m, r in low_risk:
        print(f"     [{r:.2f}] {m}")
    print(f"\n  ⚡ Recommended Command:")
    print(f"     {command}")
    print(f"{'='*60}\n")

    return result


if __name__ == "__main__":
    # Allow CLI usage: python regression_analyzer.py RegistrationController EmailService
    files = sys.argv[1:] if len(sys.argv) > 1 else ["RegistrationController", "EmailService"]
    analyze(files)
