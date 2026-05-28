import json
import argparse
import os
import sys

BACKLOG_PATH = os.path.join(os.path.dirname(__file__), "backlog.json")

# Component → Test ID mapping (mirrors qa_framework/config.json)
COMPONENT_TEST_MAP = {
    "RegistrationController": ["TC-REG-001", "TC-REG-002", "TC-REG-003", "TC-REG-004", "TC-REG-005", "TC-REG-006", "TC-REG-007", "TC-REG-008"],
    "PasswordResetController": ["TC-FP-001", "TC-FP-002", "TC-FP-003", "TC-FP-004", "TC-FP-005", "TC-FP-006"],
    "EmailService": ["TC-REG-001", "TC-REG-002", "TC-FP-001", "TC-FP-002"],
    "UserModel": ["TC-REG-001", "TC-REG-004", "TC-REG-005"],
    "TokenService": ["TC-FP-003", "TC-FP-004"],
    "PasswordValidator": ["TC-REG-003"],
}

TEST_ID_TO_FILE_MAP = {
    "TC-REG-001": "qa_framework/tests/test_registration.py::test_valid_registration",
    "TC-REG-002": "qa_framework/tests/test_registration.py::test_missing_first_name",
    "TC-REG-003": "qa_framework/tests/test_registration.py::test_weak_password",
    "TC-REG-004": "qa_framework/tests/test_registration.py::test_duplicate_email",
    "TC-REG-005": "qa_framework/tests/test_registration.py::test_missing_last_name",
    "TC-REG-006": "qa_framework/tests/test_registration.py::test_invalid_email_format",
    "TC-REG-007": "qa_framework/tests/test_registration.py::test_terms_not_accepted",
    "TC-REG-008": "qa_framework/tests/test_registration.py::test_password_mismatch",
    "TC-FP-001": "qa_framework/tests/test_forgot_password.py::test_valid_email_submission",
    "TC-FP-002": "qa_framework/tests/test_forgot_password.py::test_unregistered_email",
    "TC-FP-003": "qa_framework/tests/test_forgot_password.py::test_empty_email_field",
    "TC-FP-004": "qa_framework/tests/test_forgot_password.py::test_invalid_email_format",
    "TC-FP-005": "qa_framework/tests/test_forgot_password.py::test_success_message_displayed",
    "TC-FP-006": "qa_framework/tests/test_forgot_password.py::test_back_to_login_link",
}

RISK_THRESHOLDS = {
    "High": 0.7,
    "Medium": 0.4,
    "Low": 0.0,
}


def load_backlog():
    with open(BACKLOG_PATH, "r") as f:
        return json.load(f)


def map_work_item(work_item_id: str):
    """Map a work item ID to its linked test cases."""
    data = load_backlog()
    for item in data["work_items"]:
        if item["id"] == work_item_id:
            print(f"\n{'='*60}")
            print(f"  Work Item: {item['id']} — {item['title']}")
            print(f"  Type: {item['type']} | Priority: {item['priority']} | Sprint: {item['sprint']}")
            print(f"  Defect Rate: {item['historical_defect_rate']*100:.0f}%")
            print(f"{'='*60}")
            print("\n📋 Acceptance Criteria:")
            for i, ac in enumerate(item["acceptance_criteria"], 1):
                print(f"   {i}. {ac}")
            print("\n🧪 Linked Test Cases:")
            for tid in item["linked_test_ids"]:
                file_path = TEST_ID_TO_FILE_MAP.get(tid, "Unknown")
                print(f"   [{tid}] → {file_path}")
            return item
    print(f"[ERROR] Work item '{work_item_id}' not found in backlog.")
    return None


def analyze_changed_files(changed_files: list):
    """Given a list of changed components/files, compute impacted tests and risk scores."""
    data = load_backlog()
    heatmap = data["defect_heatmap"]

    impacted_test_ids = set()
    risk_scores = {}

    print(f"\n{'='*60}")
    print(f"  🔍 Regression Impact Analysis")
    print(f"  Changed Components: {', '.join(changed_files)}")
    print(f"{'='*60}")

    for comp in changed_files:
        comp = comp.strip()
        comp_risk = heatmap.get(comp, {}).get("risk_score", 0.3)
        defect_count = heatmap.get(comp, {}).get("defect_count", 0)

        risk_label = "High" if comp_risk >= RISK_THRESHOLDS["High"] else \
                     "Medium" if comp_risk >= RISK_THRESHOLDS["Medium"] else "Low"

        print(f"\n  📦 Component: {comp}")
        print(f"     Risk Score  : {comp_risk:.2f} ({risk_label})")
        print(f"     Defect Count: {defect_count} historical defects")

        tests = COMPONENT_TEST_MAP.get(comp, [])
        if tests:
            print(f"     Impacted Tests ({len(tests)}):")
            for tid in tests:
                print(f"       → {TEST_ID_TO_FILE_MAP.get(tid, tid)}")
                impacted_test_ids.add(tid)
                risk_scores[tid] = max(risk_scores.get(tid, 0), comp_risk)
        else:
            print(f"     No mapped test cases found for this component.")

    print(f"\n{'='*60}")
    print(f"  📊 Summary: {len(impacted_test_ids)} unique tests recommended")
    high_risk = [t for t, r in risk_scores.items() if r >= RISK_THRESHOLDS["High"]]
    medium_risk = [t for t, r in risk_scores.items() if RISK_THRESHOLDS["Medium"] <= r < RISK_THRESHOLDS["High"]]
    low_risk = [t for t, r in risk_scores.items() if r < RISK_THRESHOLDS["Medium"]]
    print(f"  🔴 High Risk   : {len(high_risk)} tests")
    print(f"  🟡 Medium Risk : {len(medium_risk)} tests")
    print(f"  🟢 Low Risk    : {len(low_risk)} tests")
    print(f"\n  💡 AI Recommendation: Run HIGH + MEDIUM risk tests immediately.")
    print(f"     Low risk tests can be deferred to nightly regression run.")
    print(f"{'='*60}\n")

    return {
        "impacted_tests": list(impacted_test_ids),
        "risk_scores": risk_scores,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
    }


def main():
    parser = argparse.ArgumentParser(description="AI-Driven Work Item to Test Case Mapper")
    parser.add_argument("--id", type=str, help="Work item ID to map (e.g. WI-001)")
    parser.add_argument("--changed-files", type=str, help="Comma-separated list of changed components")
    args = parser.parse_args()

    if args.id:
        map_work_item(args.id)
    elif args.changed_files:
        files = args.changed_files.split(",")
        result = analyze_changed_files(files)
        # Output JSON for CI/CD consumption
        output_path = os.path.join(os.path.dirname(__file__), "regression_impact.json")
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  📁 Impact report saved to: {output_path}")
    else:
        print("Usage:")
        print("  python work_item_mapper.py --id WI-001")
        print("  python work_item_mapper.py --changed-files RegistrationController,EmailService")


if __name__ == "__main__":
    main()
