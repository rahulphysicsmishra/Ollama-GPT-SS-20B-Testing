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
    / "01_wrong_answer"
)

PROBLEM_FILE = TEST_DIR / "problem.json"
STUDENT_CODE_FILE = TEST_DIR / "student_solution.py"
TEST_RESULTS_FILE = TEST_DIR / "test_results.json"


# -------------------------
# Load test data
# -------------------------

with open(PROBLEM_FILE, "r", encoding="utf-8") as file:
    problem = json.load(file)

student_code = STUDENT_CODE_FILE.read_text(
    encoding="utf-8"
)

with open(TEST_RESULTS_FILE, "r", encoding="utf-8") as file:
    test_results = json.load(file)


# -------------------------
# Get failed tests
# -------------------------

failed_tests = []

for test in test_results["tests"]:
    if not test["passed"]:
        failed_tests.append(
            {
                "input": test["input"],
                "expected": test["expected"],
                "actual": test["actual"],
            }
        )


# -------------------------
# Build prompt
# -------------------------

prompt = f"""
You are a coding tutor for beginners.

Problem:
{problem["description"]}

Student code:

```python
{student_code}
```

The code executed successfully, but some tests failed.

Failed tests:
{json.dumps(failed_tests, indent=2)}

Give the student ONE short hint that helps them discover
the mistake themselves.

Rules:

* Do not provide corrected code.
* Do not directly tell them what line to change.
* Do not solve the problem for them.
* Keep the hint beginner-friendly.
* Focus on the likely logical mistake.
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
"content": prompt,
}
],
)

# -------------------------

# Print response

# -------------------------

print("========== MODEL RESPONSE ==========\n")

print(response.message.content)

print("\n====================================")
