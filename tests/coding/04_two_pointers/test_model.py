import json
from pathlib import Path

from ollama import chat


# -------------------------
# Paths
# -------------------------

BASE_DIR = Path(__file__).resolve().parent

PROBLEM_FILE = BASE_DIR / "problem.json"
SUBMISSIONS_FILE = BASE_DIR / "submissions.json"


# -------------------------
# Load files
# -------------------------

with open(PROBLEM_FILE, "r", encoding="utf-8") as file:
    problem = json.load(file)

with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as file:
    submissions_data = json.load(file)


submissions = submissions_data["submissions"]


# -------------------------
# Build submission history
# -------------------------

submission_history = []

for submission in submissions:
    submission_history.append(
        {
            "id": submission["id"],
            "code": submission["code"]
        }
    )


# -------------------------
# Build prompt
# -------------------------

prompt = f"""
You are a coding tutor helping a beginner understand their mistakes.

Problem ID:
{problem["id"]}

Problem:
{problem["description"]}

Function name:
{problem["function_name"]}

Concepts:
{json.dumps(problem["concepts"])}

The student submitted these solutions in chronological order:

{json.dumps(submission_history, indent=2)}

Analyze the student's progression.

For EACH submission:

1. Identify the main issue in the code.
2. Explain why that approach does or does not work.
3. Explain the relevant programming concept.
4. If the code is incorrect, provide corrected code.
5. If the code is already correct, explicitly say that it is correct.
6. Keep the explanation concise and beginner-friendly.

Then compare the submissions:

- What changed between attempts?
- Did the student fix the previous issue?
- What should the student understand from this progression?

Important rules:

- Do not assume that every submission is incorrect.
- Do not invent bugs that are not present.
- Do not speculate about what the student was thinking.
- Base your analysis only on the problem and submitted code.
- Do not add unrelated advice such as type hints, docstrings,
  edge cases, or general coding style unless it is directly relevant.
- Focus on the two-pointer logic.
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