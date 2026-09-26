````markdown
# gpt-oss-lab

A small experimental repository for testing and understanding how
`gpt-oss:20b` behaves in real AI application workflows.

The goal of this repository is not to build a production application.

The goal is to experiment with a local LLM, design prompts, test different
AI behaviors, and understand what should happen before integrating the model
into larger projects.

Currently, the experiments are focused on two use cases:

- AI coding tutor
- AI guidance / reflection system

The coding tutor is currently the main experiment.

---

## Why this repository exists

I am building AI-based applications where I want to understand the model
before integrating it into the actual products.

Instead of immediately connecting an LLM to the production application,
this repository provides a small testing environment where I can:

- test the model locally
- experiment with prompts
- test coding-related responses
- test different hint strategies
- evaluate model behavior
- experiment with caching
- understand the limitations of the model
- revise the architecture before integration

The model is currently running locally through Ollama.

---

## Current Model

The current model being tested is:

```text
gpt-oss:20b
````

It is running locally through:

```text
Ollama
```

The current development environment is a Mac with Apple Silicon.

The important architectural idea is that the application should not become
tightly coupled to one model.

The eventual architecture should look roughly like:

```text
Application
     |
     v
AI Provider
     |
     v
Ollama / Local Model
     |
     v
gpt-oss:20b
```

Later, the model could be replaced without changing the rest of the
application.

---

# Repository Structure

```text
gpt-oss-lab/
│
├── .venv/
│
├── prompts/
│   ├── coding/
│   └── mindsutra/
│
├── tests/
│   ├── coding/
│   │   └── 01_wrong_answer/
│   │       ├── problem.json
│   │       ├── student_solution.py
│   │       ├── test_results.json
│   │       └── expected_hint_flow.json
│   │
│   └── mindsutra/
│
├── results/
│
├── test_model.py
│
├── README.md
│
└── .gitignore
```

Some directories are intentionally empty or only partially implemented.
The repository is being developed incrementally.

---

# How to Understand This Repository

If you are learning from this repository, don't start with the model code.

Follow the flow of the experiment.

## Step 1 — Understand the problem

Look at:

```text
tests/coding/01_wrong_answer/problem.json
```

This describes the coding problem given to the student.

Example:

```json
{
    "id": "py-basic-001",
    "title": "Check Even Number",
    "description": "Write a function called is_even that returns True if a number is even and False otherwise.",
    "function_name": "is_even",
    "language": "python",
    "difficulty": 1,
    "concepts": [
        "operators",
        "modulo",
        "boolean"
    ]
}
```

The model does not decide whether the student's code is correct.

The application/test system does that.

---

# Step 2 — Look at the student's code

Open:

```text
tests/coding/01_wrong_answer/student_solution.py
```

The current intentionally incorrect solution is:

```python
def is_even(n):
    return n % 2 == 1
```

This gives the LLM a realistic situation:

> The student attempted the problem, but their solution is wrong.

---

# Step 3 — Look at the test results

Open:

```text
tests/coding/01_wrong_answer/test_results.json
```

This represents the deterministic result of executing the student's code.

For example:

```json
{
    "passed": 0,
    "total": 2,
    "all_passed": false,
    "tests": [
        {
            "input": 4,
            "expected": true,
            "actual": false,
            "passed": false
        },
        {
            "input": 7,
            "expected": false,
            "actual": true,
            "passed": false
        }
    ]
}
```

This separation is important.

The LLM is **not the judge**.

The test system determines:

```text
Correct / Incorrect
```

The LLM is responsible for:

```text
Explanation / Hint / Guidance
```

---

# Step 4 — Understand the hint strategy

Open:

```text
tests/coding/01_wrong_answer/expected_hint_flow.json
```

This describes how the hints should become progressively more specific.

For example:

```text
Hint 1
  ↓
Conceptual

Hint 2
  ↓
More specific

Hint 3
  ↓
Point toward the relevant code

Hint 4
  ↓
Explain the mistake
```

The file does not contain the exact expected wording.

It describes the goal of each stage.

This is intentional.

We want to evaluate whether the LLM can generate useful hints rather than
hardcoding the answer.

---

# Step 5 — Run the model test

The main experiment is:

```text
test_model.py
```

Run:

```bash
python test_model.py
```

The script:

1. loads the problem
2. loads the student's code
3. loads the test results
4. identifies failed tests
5. builds a prompt
6. sends the prompt to the local model
7. prints the model's response

The model is accessed through the Ollama Python library.

---

# Current Experiment

The first experiment is intentionally simple.

The student writes:

```python
def is_even(n):
    return n % 2 == 1
```

The tests show that the answer is incorrect.

The model receives:

* the problem
* the student's code
* the failed tests
* instructions to provide a short hint

The model should help the student discover the mistake without immediately
giving the answer.

For example, a useful first hint could point the student toward the value
that `n % 2` produces for an even number.

The exact wording is generated by the model.

---

# Why We Don't Give the Solution Immediately

The goal of the coding platform is not simply:

```text
Wrong answer
    ↓
AI gives corrected code
```

Instead, the intended learning flow is:

```text
Wrong answer
    ↓
Hint 1
    ↓
Student thinks
    ↓
Student tries again
    ↓
Still wrong?
    ↓
Hint 2
    ↓
Student thinks
    ↓
Still wrong?
    ↓
Hint 3
```

The AI acts more like a tutor than an answer generator.

---

# Multi-Stage Hint System

The current experiment is moving toward a multi-stage hint system.

A possible progression is:

### Level 1 — Conceptual

Help the student think about the underlying concept.

### Level 2 — Direction

Point toward the relevant operation or idea.

### Level 3 — Code Location

Help the student identify the part of their code that should be reconsidered.

### Level 4 — Explain the Mistake

Explain what is wrong without immediately writing the complete solution.

### Level 5 — Solution

Only provide a complete solution when the product explicitly decides that
this is appropriate.

The important part is that hints are generated **one at a time**.

---

# Hint Caching

Generating a new LLM response every time is unnecessary.

The intended flow is:

```text
Student submits code
        |
        v
Run tests
        |
        v
Tests fail
        |
        v
Request Hint 1
        |
        v
LLM
        |
        v
Cache Hint 1
        |
        v
Student asks for another hint
        |
        v
Request Hint 2
        |
        v
LLM
        |
        v
Cache Hint 2
```

Previously generated hints can then be reused.

This has several benefits:

* fewer model calls
* lower latency
* lower compute usage
* consistent hints during an attempt
* easier debugging
* easier evaluation

The exact caching strategy will evolve as the experiment becomes more
realistic.

---

# Important Design Decision

The LLM should not determine whether the student's answer is correct.

The architecture should separate:

```text
Deterministic systems
        |
        +-- execute code
        +-- run tests
        +-- determine correctness


LLM
        |
        +-- explain
        +-- give hints
        +-- guide the student
```

This makes the system easier to reason about and test.

---

# What We Have Tested So Far

## Experiment 1 — Basic model interaction

We tested whether the model can respond to a simple question.

Purpose:

```text
Does the model work correctly through Ollama?
```

---

## Experiment 2 — Python explanation

We asked the model to explain a Python function.

Purpose:

```text
Can the model explain programming concepts to a beginner?
```

---

## Experiment 3 — Coding hint

We gave the model:

* a coding problem
* incorrect student code
* an instruction to give one short hint
* an instruction not to provide corrected code

The model produced a useful conceptual hint.

This established that the basic coding-tutor workflow is possible.

---

## Experiment 4 — Mindsutra-style guidance

We also tested a reflective guidance prompt.

Purpose:

```text
Can the same local model handle a different application use case?
```

This is an early experiment, not a production evaluation.

More testing is required before making conclusions about model quality.

---

# What We Are Testing Next

The next experiment focuses on multi-stage hints.

We want to test:

```text
Hint 1
   ↓
Hint 2
   ↓
Hint 3
   ↓
Hint 4
```

while checking whether the model:

* becomes progressively more specific
* avoids repeating the same hint
* avoids immediately giving the solution
* uses the student's actual code
* uses the failed tests
* remains beginner-friendly

We will also test caching so that previously generated hints do not need to
be generated again unnecessarily.

---

# Running the Repository

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd gpt-oss-lab
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

## 4. Install Ollama

Install Ollama from:

[https://ollama.com](https://ollama.com)

Then make sure it is running.

## 5. Download the model

```bash
ollama pull gpt-oss:20b
```

You can verify it with:

```bash
ollama list
```

## 6. Run the experiment

```bash
python test_model.py
```

---

# Learning Path

If you are using this repository to learn how an LLM-powered application
is designed, follow this order:

```text
1. Ollama
   ↓
2. Basic model request
   ↓
3. Prompt design
   ↓
4. Problem + student code + test results
   ↓
5. Single coding hint
   ↓
6. Multi-stage hints
   ↓
7. Hint caching
   ↓
8. Evaluation
   ↓
9. AI provider abstraction
   ↓
10. Integration into the actual application
```

The idea is to understand each layer before adding the next one.

---

# What This Repository Is Not

This repository is not currently:

* a production AI coding platform
* a benchmark for comparing every available LLM
* a complete evaluation framework
* a replacement for automated code testing
* a finished tutoring system

It is an experimental lab.

The purpose is to make AI behavior understandable before integrating it
into larger applications.

---

# Future Experiments

Possible future experiments include:

* multi-stage coding hints
* hint caching
* prompt versioning
* coding error explanations
* syntax/runtime error handling
* test-result-aware hints
* preventing premature solutions
* evaluating multiple student mistakes
* response quality evaluation
* latency measurement
* token/compute usage
* comparing different local models
* testing the same prompt across models
* integrating the final AI provider into the coding platform

---

# Philosophy

Build the smallest experiment that answers one question.

Instead of building a large AI system immediately:

```text
Question
   ↓
Small experiment
   ↓
Observe behavior
   ↓
Revise design
   ↓
Next experiment
```

This repository exists to document that process.

```
