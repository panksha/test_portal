# AI-Generated Test Case Validation Checklist

## Purpose

AI tools like ChatGPT and GitHub Copilot can generate test cases rapidly, but they are not infallible. This checklist ensures that every AI-generated test case set meets the quality bar required before being added to the automation suite.

**Mandatory rule**: A QA engineer must complete this checklist for every AI-generated test case set before committing it to the repository.

---

## Checklist

### ✅ Section 1: Coverage Completeness

- [ ] **AC-01** — Every acceptance criterion from the user story has at least one test case explicitly referencing it.
- [ ] **AC-02** — Every acceptance criterion has at least one **negative** test case (testing what happens when the criterion is violated).
- [ ] **AC-03** — All **boundary values** are explicitly tested (minimum, maximum, minimum-1, maximum+1) for any numeric or length-constrained field.
- [ ] **AC-04** — Edge cases (empty input, null values, special characters, very long strings, whitespace-only input) are covered.
- [ ] **AC-05** — There is at least one **end-to-end happy path** test covering the complete user journey.

---

### ✅ Section 2: Test Case Quality

- [ ] **QC-01** — Each test case has a **unique ID** that follows the naming convention (e.g., TC-MODULE-NNN).
- [ ] **QC-02** — Each test case title is **descriptive and action-oriented** (e.g., "Verify registration fails when email already exists" not "Test duplicate email").
- [ ] **QC-03** — **Preconditions** are fully and clearly stated. A tester can set up the test without making assumptions.
- [ ] **QC-04** — **Test steps** are numbered, atomic, and unambiguous. Each step contains exactly one action.
- [ ] **QC-05** — **Expected results** are **specific and verifiable** — they describe observable outcomes, not vague states (e.g., "Error message 'Email already in use' appears below the email field" not "Error is shown").
- [ ] **QC-06** — **Priority** is assigned (High/Medium/Low) and is justifiable based on business impact.
- [ ] **QC-07** — There are **no duplicate test cases** (two cases covering the exact same scenario).
- [ ] **QC-08** — Each test case can be executed **independently** without relying on the result or state of another test case.

---

### ✅ Section 3: AI-Specific Validation

- [ ] **AI-01** — **No hallucinated fields**: All form fields, buttons, URLs, and UI elements referenced in the test steps actually exist in the application.
- [ ] **AI-02** — **No hallucinated behavior**: The expected results describe what the application *actually* does, not what the AI *assumed* it does. This requires a manual review against the actual application.
- [ ] **AI-03** — **Error messages are accurate**: Any specific error message text in the expected results matches the actual application error messages.
- [ ] **AI-04** — **Technology constraints respected**: Test steps do not assume features or capabilities that don't exist in the tech stack.
- [ ] **AI-05** — **Security and data handling**: No test case contains real personally identifiable information (PII) or production credentials. Use test data only.

---

### ✅ Section 4: Automation Readiness

- [ ] **AR-01** — Each test case is structured in a way that maps directly to an automatable Selenium action sequence.
- [ ] **AR-02** — All UI elements referenced have identifiable locators (ID, name, CSS class, or XPath-navigable structure).
- [ ] **AR-03** — The test case does not rely on timing-based assumptions (e.g., "wait 5 seconds") — instead, use explicit waits.
- [ ] **AR-04** — Data-driven scenarios are parameterized, not duplicated as separate test cases.

---

### ✅ Section 5: Reviewer Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Engineer (Author) | | | |
| QA Lead (Reviewer) | | | |
| BA/Product (Requirement owner) | | | |

---

## Scoring

| Score | Action |
|-------|--------|
| 100% Checked | ✅ Approved — commit to test suite |
| 85–99% Checked | ⚠️ Conditional Approval — fix open items within 24 hours |
| < 85% Checked | ❌ Rejected — return to QA engineer for rework |

---

## Common AI Test Generation Mistakes (Know These!)

1. **Generic expected results** — AI often writes "User is redirected to next page" without specifying which page or what's on it.
2. **Missing negative tests** — AI naturally focuses on happy paths. Always explicitly ask for negative scenarios.
3. **Hallucinated error messages** — AI invents plausible-sounding error messages that don't match the actual UI. Always verify.
4. **Missing preconditions** — AI assumes the app is "in a clean state" without specifying how to achieve that.
5. **Overly broad test cases** — AI sometimes generates one test case covering too many conditions. Split these into atomic tests.
