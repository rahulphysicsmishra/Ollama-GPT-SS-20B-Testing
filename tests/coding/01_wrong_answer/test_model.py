import hashlib
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
HINT_FLOW_FILE = TEST_DIR / "expected_hint_flow.json"
CACHE_FILE = TEST_DIR / "hint_cache.json"


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

with open(HINT_FLOW_FILE, "r", encoding="utf-8") as file:
    hint_flow = json.load(file)


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
# Load cache
# -------------------------

if CACHE_FILE.exists():
    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        hint_cache = json.load(file)
else:
    hint_cache = {}


# -------------------------
# Create cache key
# -------------------------

def create_cache_key(hint_level):
    cache_data = {
        "problem_id": problem["id"],
        "student_code": student_code,
        "failed_tests": failed_tests,
        "hint_level": hint_level,
    }

    cache_string = json.dumps(
        cache_data,
        sort_keys=True
    )

    return hashlib.sha256(
        cache_string.encode("utf-8")
    ).hexdigest()


# -------------------------
# Find hint goal
# -------------------------

def get_hint_goal(level):
    for hint in hint_flow["hint_levels"]:
        if hint["level"] == level:
            return hint["goal"]

    return None


# -------------------------
# Get next hint
# -------------------------

def get_next_hint(level, previous_hints):

    goal = get_hint_goal(level)

    if goal is None:
        print("\nNo more hint levels available.")
        return None

    cache_key = create_cache_key(level)

    # -------------------------
    # Check cache
    # -------------------------

    if cache_key in hint_cache:

        print("\nUsing cached hint...\n")

        return hint_cache[cache_key]

    # -------------------------
    # Build previous hints
    # -------------------------

    previous_hints_text = ""

    if previous_hints:
        previous_hints_text = f"""
Previous hints already given:

{json.dumps(previous_hints, indent=2)}

Do not repeat these hints.
Make this hint more specific than the previous hints.
"""

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

This is hint level {level}.

Goal for this hint:
{goal}

{previous_hints_text}

Rules:

Give ONLY ONE short hint.
Do not provide corrected code.
Do not directly tell the student what line to change.
Do not solve the problem completely.
Keep the hint beginner-friendly.
Help the student discover the mistake themselves.
"""

    print("\nSending request to gpt-oss:20b...\n")

    response = chat(
        model="gpt-oss:20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    hint_text = response.message.content.strip()

    hint_cache[cache_key] = {
        "level": level,
        "text": hint_text,
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            hint_cache,
            file,
            indent=4,
        )

    return hint_cache[cache_key]


print("\n====================================")
print(" AI CODING HINT TEST")
print("====================================")

print(f"\nProblem: {problem['title']}")
print(f"Student code:\n{student_code}")

print("\nFailed tests:")
print(json.dumps(failed_tests, indent=2))

previous_hints = []
current_level = 1

while True:
    print("\n------------------------------------")
    print("Options:")
    print("1. Get next hint")
    print("2. Exit")
    print("------------------------------------")

    choice = input("\nChoose: ").strip()

    if choice == "2":
        print("\nExiting.")
        break

    if choice != "1":
        print("\nPlease choose 1 or 2.")
        continue

    hint = get_next_hint(
        current_level,
        previous_hints,
    )

    if hint is None:
        break

    print(f"\n========== HINT {current_level} ==========\n")
    print(hint["text"])

    previous_hints.append(hint)

    current_level += 1

    if current_level > len(hint_flow["hint_levels"]):
        print("\nNo more hints available.")
        break
