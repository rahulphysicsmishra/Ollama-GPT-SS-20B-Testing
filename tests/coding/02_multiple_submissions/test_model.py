import json
from pathlib import Path

from ollama import chat


# -------------------------
# Paths
# -------------------------

BASE_DIR = Path(__file__).resolve().parent

TEST_DIR = (
    BASE_DIR
    / "tests"
    / "coding"
    / "02_multiple_submissions"
)

PROBLEM_FILE = TEST_DIR / "problem.json"
SUBMISSIONS_FILE = TEST_DIR / "submissions.json"
TEST_RESULTS_FILE = TEST_DIR / "test_results.json"


# -------------------------
# Load files
# -------------------------

with open(PROBLEM_FILE, "r", encoding="utf-8") as file:
    problem = json.load(file)

with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as file:
    submissions_data = json.load(file)

with open(TEST_RESULTS_FILE, "r", encoding="utf-8") as file:
    test_results_data = json.load(file)


submissions = submissions_data["submissions"]
test_results = test_results_data["submissions"]


# -------------------------
# Build submission data
# -------------------------

submission_history = []

for submission in submissions:
    submission_id = submission["id"]

    matching_result = None

    for result in test_results:
        if result["id"] == submission_id:
            matching_result = result
            break

    if matching_result is None:
        print(
            f"Could not find test results for submission {submission_id}."
        )
        continue

    failed_tests = []

    for test in matching_result["tests"]:
        if not test["passed"]:
            failed_tests.append(
                {
                    "input": test["input"],
                    "expected": test["expected"],
                    "actual": test["actual"]
                }
            )

    submission_history.append(
        {
            "submission_id": submission_id,
            "code": submission["code"],
            "failed_tests": failed_tests
        }
    )


# -------------------------
# Build prompt
# -------------------------

prompt = f"""
You are a coding tutor for beginners.

Analyze the student's failed submissions for the following problem.

Problem:
{problem["description"]}

Function name:
{problem["function_name"]}

Here are the student's submissions in chronological order:

{json.dumps(submission_history, indent=2)}

For EACH submission:

1. Explain what the student was trying to do.
2. Identify the exact mistake.
3. Explain why the failed tests fail.
4. Provide corrected code.
5. Briefly explain why the corrected code works.

Important rules:

- Analyze each submission separately.
- Do not assume that all submissions have the same mistake.
- Pay attention to the actual failed test results.
- If a submission has a syntax error, explain the syntax error.
- If a submission has a logical error, explain the logical error.
- Keep the explanation beginner-friendly.
- Show complete corrected code for each submission.
- Do not skip any submission.

At the end, briefly explain how the student's mistakes changed across
the three submissions.
"""


# -------------------------
# Send request to Ollama
# -------------------------

print("Sending request to gpt-oss:20b...\n")

response = chat(
    model="gpt-oss:20b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


# -------------------------
# Print response
# -------------------------

print("====================================")
print("MODEL RESPONSE")
print("====================================\n")

print(response.message.content)

print("\n====================================")