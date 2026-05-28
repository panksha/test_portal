# AI Test Generation Prompt — Chain-of-Thought Template

## How to Use This Prompt

Copy and paste this prompt into ChatGPT (GPT-4), GitHub Copilot Chat, or Google Gemini. Replace the `[PLACEHOLDER]` sections with your actual requirement details.

---

## The Prompt

```
SYSTEM: You are a Senior QA Automation Architect. Generate structured test cases following industry best practices.

ROLE: Act as a QA Lead responsible for sign-off on the test suite before sprint release.

CONTEXT:
  Application: [Application Name — e.g., "Corporate Employee Portal"]
  Module: [Module Name — e.g., "User Registration"]
  Technology Stack: Python Flask backend, HTML/CSS/JS frontend, REST API
  Test Environment: Local staging server at http://localhost:5000

REQUIREMENT (User Story):
  [Paste the full user story or requirement text here]
  
ACCEPTANCE CRITERIA:
  [List each acceptance criterion, numbered AC-001, AC-002, etc.]

CHAIN OF THOUGHT — Think step by step:
  Step 1: Identify all actors and user flows described in the requirement.
  Step 2: For each acceptance criterion, identify: 
            (a) the happy path scenario, 
            (b) at least one negative/failure scenario, 
            (c) any boundary value or edge case.
  Step 3: Identify any implicit requirements (security, accessibility, performance).
  Step 4: Check for gaps — are there scenarios the acceptance criteria don't explicitly cover but are clearly expected behavior?
  Step 5: Generate the final test case table.

CONSTRAINTS:
  - Generate at least 8 test cases for this feature.
  - Include: valid input tests, invalid input tests, boundary value tests, negative tests, UI validation tests.
  - Use the following format for each test case:
      TC ID | Title | Preconditions | Steps | Expected Result | Priority (High/Med/Low) | Risk | AC Reference
  - Mark security-related test cases with [SECURITY] tag.
  - Mark accessibility test cases with [A11Y] tag.

VALIDATION INSTRUCTION:
  After generating the test cases, self-review them against this checklist:
  ✓ Every acceptance criterion has at least one test case referencing it
  ✓ At least one negative test case per acceptance criterion
  ✓ Boundary values are explicitly tested
  ✓ No duplicate test cases
  ✓ Each test case is independently executable without depending on another test
  
  If any checklist item fails, add the missing test cases before finalizing output.

OUTPUT FORMAT: Markdown table
```

---

## Example — Filled Prompt for "User Registration"

```
SYSTEM: You are a Senior QA Automation Architect. Generate structured test cases.

CONTEXT:
  Application: Corporate Employee Portal
  Module: User Registration
  Technology Stack: Python Flask, HTML/CSS/JS

REQUIREMENT:
  As a new user, I want to register an account using my name, email, and password 
  so that I can access the application.

ACCEPTANCE CRITERIA:
  AC-001: User can register with valid first name, last name, email, and password
  AC-002: Password must be ≥8 chars with 1 uppercase, 1 number, 1 special character
  AC-003: Duplicate email addresses must be rejected
  AC-004: Empty fields must show validation errors
  AC-005: Terms & Conditions checkbox must be checked
  AC-006: Successful registration redirects to confirmation page

CHAIN OF THOUGHT: [as above]

CONSTRAINTS: [as above]
```

---

## Expected AI Output (Sample)

| TC ID | Title | Preconditions | Steps | Expected Result | Priority | Risk | AC Ref |
|-------|-------|--------------|-------|-----------------|----------|------|--------|
| TC-REG-001 | Valid Registration — All Fields Correct | App running, fresh session | 1. Navigate to /register 2. Enter valid data in all fields 3. Check T&C 4. Click Register | Success message shown, redirected to confirmation | High | High | AC-001, AC-006 |
| TC-REG-002 | Missing First Name | App running | 1. Navigate to /register 2. Leave First Name blank 3. Fill other fields 4. Click Register | Error: "First name is required" | High | Medium | AC-004 |
| TC-REG-003 | Weak Password — No Special Character | App running | 1. Enter password "Password1" (no special char) 2. Submit | Error: "Password must contain a special character" | High | High | AC-002 |

---

## Pro Tips for Better AI-Generated Test Cases

1. **Be specific in context** — The more details you give about the module and tech stack, the more relevant the output.
2. **Always use Chain-of-Thought** — Forces the AI to reason before generating, reducing hallucinations.
3. **Request self-validation** — The self-review checklist instruction catches gaps automatically.
4. **Iterate with follow-ups** — After initial generation, ask: *"Add 3 more edge cases for the password validation field."*
5. **Human review is mandatory** — AI-generated tests must be reviewed for: test independence, correctness of expected results, and alignment with actual system behavior.
