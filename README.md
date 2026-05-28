# AI-Driven QA Automation Demo Framework

> **Prepared for: Pankaj | Client Interview Preparation**
> A complete, runnable AI-driven QA automation prototype demonstrating the full lifecycle from AI test generation to CI/CD-integrated test execution with self-healing locators.

---

## 🚀 Quick Start (2 minutes)

### Step 1: Install Dependencies
```bash
cd "c:\Users\Admin\Documents\Python_Projects\New_Job"
pip install -r requirements.txt
```

### Step 2: Launch Everything
```bash
python run.py
```

This starts:
- 🌐 **Target Portal** → `http://localhost:5000`
- 🖥️ **Interview Dashboard** → `http://localhost:8000`

### Step 3: Open the Dashboard
Open your browser and go to: **`http://localhost:8000`**

---

## 📁 Project Structure

```
New_Job/
├── run.py                    # ← START HERE (launches everything)
├── requirements.txt
├── README.md
├── INTERVIEW_GUIDE.md        # ← Interview talking points cheat sheet
│
├── .github/workflows/        # Real GitHub Actions CI/CD pipeline
│   └── qa-pipeline.yml
├── azure-pipelines.yml       # Real Azure DevOps pipeline
│
├── ai_prompts/               # AI prompt templates to show the client
│   ├── system_prompt.md
│   ├── test_generation_prompt.md
│   ├── regression_prompt.md
│   └── validation_checklist.md
│
├── work_items/               # Jira/ADO work item simulation
│   ├── backlog.json
│   └── work_item_mapper.py
│
├── target_app/               # The web app being tested (Flask)
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── qa_framework/             # Selenium automation framework
│   ├── config.json           # Locator repository with fallbacks
│   ├── conftest.py           # Fixtures + screenshot on failure
│   ├── self_healing_engine.py
│   ├── regression_analyzer.py
│   ├── pages/                # Page Object Model
│   └── tests/                # 14 test cases
│
└── showcase_dashboard/       # Interview control center
    ├── index.html
    ├── assets/
    └── data/
```

---

## 🧪 Running Tests Manually

```bash
# Run all 14 tests
pytest qa_framework/tests/ -v --html=qa_framework/reports/html/report.html

# Run registration tests only
pytest qa_framework/tests/test_registration.py -v

# Run forgot password tests only
pytest qa_framework/tests/test_forgot_password.py -v

# Run with headed browser (visible)
pytest qa_framework/tests/ -v  # headless=false in config.json
```

---

## 🔧 Self-Healing Demo

1. Open `http://localhost:8000` → **Live Demo** tab
2. Enable **"Simulate Broken Locators"** toggle
3. Click **"Run Tests"**
4. Watch the Self-Healing Engine intercept the locator failure and heal it!

---

## 🔬 Regression Analysis

```bash
# Analyze impact of changed components
python work_items/work_item_mapper.py --changed-files "RegistrationController,EmailService"

# Map a work item to its tests
python work_items/work_item_mapper.py --id WI-001

# Direct regression analysis
python qa_framework/regression_analyzer.py RegistrationController EmailService
```

---

## 📊 Viewing Reports

After running tests, open:
```
qa_framework/reports/html/report.html
```

Self-healing event log:
```
qa_framework/reports/healing_log.json
```

---

## 🔗 GitHub Actions CI/CD Pipeline

The framework is fully integrated with **GitHub Actions** for automated regression testing on every push or pull request to the `main` branch.

### How it runs in the cloud:
* **Workflow File:** [qa-pipeline.yml](file:///.github/workflows/qa-pipeline.yml)
* **Triggers:** Triggers automatically on any code `push` or `pull_request` to `main`, `develop`, or `feature/*` branches.
* **On-Demand Manual Trigger:** Supports manual trigger (`workflow_dispatch`) with custom options to run specific test suites and toggle **Simulate Broken Locators** directly in the cloud.
* **Continuous Testing:** Spins up a clean Linux virtual machine (`ubuntu-latest`), starts the Flask app, and executes all Selenium test cases using a **headless Chrome browser**.
* **Visual Step Logger:** Logs each E2E test step-by-step (e.g., Chrome opens, typing fields, waiting for AJAX success, reading message box) directly in the GitHub Actions terminal logs!
* **Artifacts Archiving:** Automatically captures and uploads `HTMLTestReport` and `FailureScreenshots` (only on test failure) directly to the pipeline run summary page for easy download!

---

## 🐞 Automated Jira Tool Integration

Our pipeline includes a DevSecOps **automated bug-raising loop** to automatically create tickets in Jira when a test fails in the CI/CD environment.

### Setup Instructions:
1. **Create an API Token:** Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and click **Create API Token**.
2. **Configure GitHub Secrets:** Add the following three secure variables under **Settings > Secrets and variables > Actions** in your GitHub repository:
   * `JIRA_BASE_URL` - Your Jira Cloud URL (e.g., `https://yourorg.atlassian.net`)
   * `JIRA_USER_EMAIL` - Your Atlassian email address (e.g., `yourname@example.com`)
   * `JIRA_API_TOKEN` - The secure API Token you generated in Step 1.
3. **Execution:** The post-execution job in the pipeline checks the run status. If `qa-tests` fails (`if: failure()`), the runner immediately makes a secure `POST /rest/api/3/issue` REST API call to your Jira instance to file a high-priority bug ticket containing build links, branch names, and error details automatically!

---

## 🔗 Key URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Interview Showcase Dashboard |
| http://localhost:5000 | Target Web Portal |
| http://localhost:5000/register | User Registration Form |
| http://localhost:5000/forgot-password | Forgot Password Form |
| http://localhost:5000/api/break-locators | Toggle locator breakage (POST) |

---

## 💡 Interview Tips

See [INTERVIEW_GUIDE.md](./INTERVIEW_GUIDE.md) for the complete talking points guide.
