"""
conftest.py — PyTest Configuration & Fixtures
- WebDriver setup and teardown
- Screenshot on failure
- HTML report configuration
"""

import os
import json
import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def pytest_configure(config):
    """Configure pytest-html report metadata."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(REPORTS_DIR, "html"), exist_ok=True)


def pytest_runtest_setup(item):
    """Reset step logger before each test."""
    try:
        from qa_framework.step_logger import StepLogger
        StepLogger.reset(item.name)
    except Exception:
        pass


def pytest_html_report_title(report):
    report.title = "AI-Driven QA Automation — Test Execution Report"


# ── WebDriver Fixture ──────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver(request):
    """
    Setup and teardown for Selenium WebDriver.
    Supports Chrome (default) and Edge.
    Reads config from qa_framework/config.json.
    """
    cfg = _load_config()
    browser = os.environ.get("BROWSER", cfg.get("browser", "chrome")).lower()
    headless = os.environ.get("HEADLESS", str(cfg.get("headless", False))).lower() == "true"

    if browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1366,768")
        driver_path = EdgeChromiumDriverManager().install()
        if not (driver_path.endswith("msedgedriver.exe") or driver_path.endswith("msedgedriver")):
            dir_name = os.path.dirname(driver_path)
            win_path = os.path.join(dir_name, "msedgedriver.exe")
            nix_path = os.path.join(dir_name, "msedgedriver")
            if os.path.exists(win_path):
                driver_path = win_path
            elif os.path.exists(nix_path):
                driver_path = nix_path
        service = EdgeService(driver_path)
        drv = webdriver.Edge(service=service, options=options)
    else:
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1366,768")
        driver_path = ChromeDriverManager().install()
        if not (driver_path.endswith("chromedriver.exe") or driver_path.endswith("chromedriver")):
            dir_name = os.path.dirname(driver_path)
            win_path = os.path.join(dir_name, "chromedriver.exe")
            nix_path = os.path.join(dir_name, "chromedriver")
            if os.path.exists(win_path):
                driver_path = win_path
            elif os.path.exists(nix_path):
                driver_path = nix_path
        service = ChromeService(driver_path)
        drv = webdriver.Chrome(service=service, options=options)

    drv.implicitly_wait(0)  # Use explicit waits only
    drv.maximize_window()

    yield drv

    # ── Teardown ──────────────────────────────────────────────────────────────
    drv.quit()


# ── Screenshot on Failure Hook ──────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = item.name.replace("[", "_").replace("]", "_").replace(" ", "_")
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"FAIL_{test_name}_{timestamp}.png")
            try:
                driver.save_screenshot(screenshot_path)
                logging.info(f"[Screenshot] Saved: {screenshot_path}")

                # Embed in pytest-html report
                if hasattr(report, "extras"):
                    import pytest_html
                    report.extras.append(pytest_html.extras.image(screenshot_path))
                    report.extras.append(pytest_html.extras.url(driver.current_url, "Page URL"))
            except Exception as e:
                logging.warning(f"[Screenshot] Failed to capture: {e}")


# ── Environment Info for Report ────────────────────────────────────────────

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        "<p><b>Framework:</b> Python + Selenium + PyTest (POM Architecture)</p>",
        "<p><b>Self-Healing:</b> Enabled — Locator Repository with 4-layer fallback</p>",
        "<p><b>Target App:</b> http://localhost:5000</p>",
        "<p><b>CI/CD:</b> GitHub Actions + Azure DevOps</p>",
    ])
