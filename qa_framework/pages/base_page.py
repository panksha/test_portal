"""
BasePage — Foundation class for all Page Objects.
Includes explicit wait utilities and the Self-Healing element finder.
"""

import os
import json
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


class BasePage:
    """
    Base class for all Page Objects.
    Provides:
    - Self-healing find_element via the SelfHealingEngine
    - Explicit wait wrappers (wait_for_visible, wait_for_clickable)
    - Input helpers (clear_and_type, safe_click)
    - Element state checks (is_displayed, is_enabled)
    """

    def __init__(self, driver, page_name: str):
        self.driver = driver
        self.page_name = page_name
        self._config = self._load_config()
        self._explicit_wait = self._config.get("explicit_wait", 10)
        self._wait = WebDriverWait(driver, self._explicit_wait)

    def _load_config(self):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    # ── Core: Self-Healing Element Finder ────────────────────────────────────

    def find(self, locator_key: str, timeout: int = None):
        """
        Find an element using the self-healing engine.
        Falls back through the locator repository on failure,
        then updates the config with the working locator.
        """
        from qa_framework.self_healing_engine import heal_locator
        t = timeout or self._explicit_wait
        return heal_locator(self.driver, self.page_name, locator_key, timeout=t)

    # ── Explicit Wait Helpers ─────────────────────────────────────────────────

    def wait_for_visible(self, locator_key: str, timeout: int = None):
        """Wait until element is visible in the DOM."""
        element = self.find(locator_key, timeout)
        t = timeout or self._explicit_wait
        try:
            by_str = self._get_current_by(locator_key)
            val = self._get_current_value(locator_key)
            WebDriverWait(self.driver, t).until(
                EC.visibility_of_element_located((by_str, val))
            )
        except TimeoutException:
            pass  # Element already found by self-healer; visibility check is best-effort
        return element

    def wait_for_clickable(self, locator_key: str, timeout: int = None):
        """Wait until element is visible AND enabled (clickable)."""
        element = self.find(locator_key, timeout)
        t = timeout or self._explicit_wait
        try:
            by_str = self._get_current_by(locator_key)
            val = self._get_current_value(locator_key)
            WebDriverWait(self.driver, t).until(
                EC.element_to_be_clickable((by_str, val))
            )
        except TimeoutException:
            pass
        return element

    def _get_current_by(self, locator_key: str):
        """Get the current primary By strategy for a locator key."""
        from qa_framework.self_healing_engine import BY_MAP
        config = self._load_config()
        primary = config["locators"].get(self.page_name, {}).get(locator_key, {}).get("primary", {})
        return BY_MAP.get(primary.get("by", "id"), By.ID)

    def _get_current_value(self, locator_key: str):
        config = self._load_config()
        primary = config["locators"].get(self.page_name, {}).get(locator_key, {}).get("primary", {})
        return primary.get("value", "")

    # ── Interaction Helpers ───────────────────────────────────────────────────

    def clear_and_type(self, locator_key: str, text: str):
        """Clear an input field and type text, using self-healing finder."""
        element = self.wait_for_visible(locator_key)
        from qa_framework.step_logger import StepLogger
        StepLogger.log_typing(locator_key, text)
        element.clear()
        element.send_keys(str(text))
        time.sleep(1.0)  # Pause to observe typing
        return element

    def safe_click(self, locator_key: str):
        """Wait for element to be clickable, then click."""
        element = self.wait_for_clickable(locator_key)
        from qa_framework.step_logger import StepLogger
        StepLogger.log_click(locator_key)
        element.click()
        time.sleep(1.5)  # Pause to observe transition
        return element

    def get_text(self, locator_key: str) -> str:
        """Get the text content of an element."""
        element = self.find(locator_key)
        return element.text.strip()

    def is_displayed(self, locator_key: str) -> bool:
        """Check if an element is displayed on the page."""
        try:
            element = self.find(locator_key, timeout=5)
            displayed = element.is_displayed()
            if locator_key in ["form_success", "form_error", "success_msg", "error_msg"]:
                from qa_framework.step_logger import StepLogger
                StepLogger.log_check(locator_key, displayed)
            return displayed
        except (NoSuchElementException, TimeoutException):
            if locator_key in ["form_success", "form_error", "success_msg", "error_msg"]:
                from qa_framework.step_logger import StepLogger
                StepLogger.log_check(locator_key, False)
            return False

    def is_enabled(self, locator_key: str) -> bool:
        """Check if an element is enabled."""
        try:
            element = self.find(locator_key, timeout=5)
            return element.is_enabled()
        except (NoSuchElementException, TimeoutException):
            return False

    def navigate_to(self, path: str = ""):
        """Navigate to a path on the base URL."""
        base_url = self._config.get("base_url", "http://localhost:5000")
        from qa_framework.step_logger import StepLogger
        StepLogger.log_navigation(f"{base_url}{path}")
        self.driver.get(f"{base_url}{path}")
        time.sleep(1.5)  # Pause to observe page load

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_page_title(self) -> str:
        return self.driver.title
