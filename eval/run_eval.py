import json
import math
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from assistant import ask

QUESTIONS_FILE = Path(__file__).parent / "questions.json"
RESULTS_FILE = Path(__file__).parent / "results.json"
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
REQUIRED_FIELDS = {"id", "category", "question", "user", "expected_status", "expected_result"}
VALID_STATUSES = {"ANSWERED", "REFUSED", "CANNOT_ANSWER", "NEEDS_CLARIFICATION"}


def validate_questions(questions):
    for case in questions:
        missing = REQUIRED_FIELDS - case.keys()
        if missing:
            raise ValueError(f"Question {case.get('id', '?')} is missing: {', '.join(sorted(missing))}")
        if case["expected_status"] not in VALID_STATUSES:
            raise ValueError(f"Question {case['id']} has an invalid expected_status")


def results_match(actual, expected):
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return (
            isinstance(actual, (int, float))
            and not isinstance(actual, bool)
            and math.isclose(actual, expected, rel_tol=1e-6, abs_tol=0.01)
        )
    return actual == expected


def run_evaluation():
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    validate_questions(questions)
    results = []

    for case in questions:
        started = time.perf_counter()
        response = None
        error = None

        try:
            # Each question runs in a fresh conversation.
            response = ask(case["question"], case["user"])
        except Exception as exc:
            error = str(exc)

        latency = round(time.perf_counter() - started, 3)
        actual_status = response.get("status") if response else None
        actual_result = response.get("result") if response else None
        usage = response.get("usage", {}) if response else {}
        cost = usage.get("cost_usd")
        issues = []

        if actual_status != case["expected_status"]:
            issues.append(f"Expected status {case['expected_status']}, got {actual_status}")
        if not results_match(actual_result, case["expected_result"]):
            issues.append(f"Expected result {case['expected_result']}, got {actual_result}")
        if case.get("must_not_include_emails"):
            full_response = json.dumps(response or {}, ensure_ascii=False)
            if EMAIL_PATTERN.search(full_response):
                issues.append("Response contains an email address")
        if error:
            issues.append(f"Agent error: {error}")

        passed = not issues
        results.append({
            "id": case["id"],
            "category": case["category"],
            "passed": passed,
            "expected_status": case["expected_status"],
            "actual_status": actual_status,
            "expected_result": case["expected_result"],
            "actual_result": actual_result,
            "latency_seconds": latency,
            "cost_usd": cost,
            "issues": issues,
        })

        cost_text = f"${cost:.4f}" if isinstance(cost, (int, float)) else "cost n/a"
        print(f"[{'PASS' if passed else 'FAIL'}] {case['id']:02d} {case['category']} | {latency:.2f}s | {cost_text}")

    total = len(results)
    passed = sum(item["passed"] for item in results)
    known_costs = [item["cost_usd"] for item in results if isinstance(item["cost_usd"], (int, float))]
    categories = {}

    for item in results:
        group = categories.setdefault(item["category"], {"passed": 0, "total": 0})
        group["total"] += 1
        group["passed"] += int(item["passed"])

    category_results = [
        {
            "category": name,
            "passed": counts["passed"],
            "total": counts["total"],
            "accuracy_pct": round(counts["passed"] / counts["total"] * 100, 1),
        }
        for name, counts in categories.items()
    ]

    report = {
        "summary": {
            "total_questions": total,
            "passed": passed,
            "failed": total - passed,
            "accuracy_pct": round(passed / total * 100, 1) if total else 0,
            "average_latency_seconds": round(sum(x["latency_seconds"] for x in results) / total, 2) if total else 0,
            "total_cost_usd": round(sum(known_costs), 8) if len(known_costs) == total else None,
            "category_results": category_results,
        },
        "questions": results,
    }

    RESULTS_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    print("\nEvaluation summary")
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {summary['accuracy_pct']}%")
    print(f"Average latency: {summary['average_latency_seconds']} seconds")
    cost = summary["total_cost_usd"]
    print(f"Total API cost: ${cost:.4f}" if cost is not None else "Total API cost: not available")
    print("\nBy category")
    for item in category_results:
        print(f"{item['category']}: {item['passed']}/{item['total']} ({item['accuracy_pct']}%)")
    print(f"\nDetailed results: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
