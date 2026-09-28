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
You are a coding tutor helping a beginner learn from their attempts.

Problem ID:
{problem["id"]}

Problem:
{problem["description"]}

Function name:
{problem["function_name"]}

The student submitted the following solutions in chronological order:

{json.dumps(submission_history, indent=2)}

Analyze the student's progression across these submissions.

For EACH submission:

1. Explain what the student is trying to do.
2. Identify the likely mistake or issue in the code.
3. Explain the programming concept involved.
4. Show corrected code.
5. Explain why the corrected code works.

Then compare the submissions and explain:

- What changed from one submission to the next?
- Did the student move closer to the correct solution?
- What misunderstanding appears to remain?
- What should the student think about next?

Keep the explanation beginner-friendly.

Do not assume that all submissions have the same mistake.
Analyze the actual code in each submission.
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