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
