# -*- coding: utf-8 -*-
"""
Step Logger Utility — qa_framework/step_logger.py
Provides real-time console logging for Selenium actions during test execution,
fully matching the requested step-by-step flow with 100% ASCII console safety.
"""

import sys
import time
import logging

logger = logging.getLogger(__name__)

LOCATOR_NAMES = {
    "first_name": "First Name field",
    "last_name": "Last Name field",
    "email": "Email field",
    "password": "Password field",
    "confirm_password": "Confirm Password field",
    "terms": "I agree to Terms checkbox",
    "register_btn": "Create Account button",
    "send_btn": "Send Password Reset Link button",
    "back_to_login": "Back to Login link",
    "form_success": "Success Message div",
    "form_error": "Error Message div",
    "success_msg": "Success Message div",
    "error_msg": "Error Message div",
}

class StepLogger:
    step_count = 0
    test_name = ""
    logged_assertion = False

    @classmethod
    def reset(cls, test_name):
        cls.step_count = 0
        cls.test_name = test_name
        cls.logged_assertion = False
        print(f"\n\033[1m\033[95m=== Running Test Case: {test_name} ===\033[0m")
        sys.stdout.flush()

    @classmethod
    def log_step(cls, left, right):
        cls.step_count += 1
        print(f"\033[1m\033[97mStep {cls.step_count:2d}:\033[0m  {left:<27} \033[90m->\033[0m {right}")
        sys.stdout.flush()

    @classmethod
    def log_navigation(cls, url):
        cls.log_step("Chrome opens", f"navigates to \033[94m{url}\033[0m")

    @classmethod
    def log_typing(cls, locator_key, value):
        field_name = LOCATOR_NAMES.get(locator_key, locator_key)
        if "password" in locator_key.lower():
            value_str = "password"
            mask_str = "******"
        else:
            value_str = f"\"{value}\""
            mask_str = value
            if len(mask_str) > 25:
                mask_str = mask_str[:22] + "..."

        left = f"Selenium types {value_str}"
        right = f"into {field_name}  [ \033[36m{mask_str}\033[0m ]"
        cls.log_step(left, right)

    @classmethod
    def log_click(cls, locator_key):
        field_name = LOCATOR_NAMES.get(locator_key, locator_key)
        if locator_key == "terms":
            left = "Selenium clicks checkbox"
            right = "\033[32m[x] I agree to Terms\033[0m"
            cls.log_step(left, right)
        else:
            left = "Selenium clicks button"
            right = f"\"{field_name}\" clicked"
            cls.log_step(left, right)

            # Automatically generate AJAX transition logs for submit actions
            if locator_key in ["register_btn", "send_btn"]:
                cls.log_step("JavaScript sends AJAX POST", "Flask validates data")
                cls.log_step("Flask returns response", "JavaScript shows div on screen")

    @classmethod
    def log_check(cls, locator_key, is_success):
        if cls.logged_assertion:
            return
        cls.logged_assertion = True

        time.sleep(2.0)  # Pause to let the viewer see the success/error message box on the GUI first!
        left = "Selenium reads the div text"
        if is_success:
            right = "Test asserts expected message \033[92m[PASS]\033[0m"
        else:
            right = "Test asserts expected message \033[91m[FAIL]\033[0m"

        cls.log_step(left, right)
