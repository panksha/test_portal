"""
ForgotPasswordPage — Page Object for the Forgot Password form.
"""

from qa_framework.pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    """
    Page Object Model for /forgot-password page.
    Encapsulates all locators and actions for the forgot password form.
    """

    PAGE_NAME = "forgot_password"
    PATH = "/forgot-password"

    def __init__(self, driver):
        super().__init__(driver, self.PAGE_NAME)

    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self):
        """Navigate to the forgot password page."""
        self.navigate_to(self.PATH)
        return self

    # ── Page Actions ──────────────────────────────────────────────────────────

    def enter_email(self, email: str):
        self.clear_and_type("email", email)
        return self

    def click_send_reset(self):
        self.safe_click("send_btn")
        return self

    def click_back_to_login(self):
        self.safe_click("back_to_login")
        return self

    # ── Composite Actions ─────────────────────────────────────────────────────

    def submit_reset_request(self, email: str):
        """Enter email and submit the forgot password form."""
        self.enter_email(email)
        self.click_send_reset()
        return self

    # ── Assertions / State Checks ─────────────────────────────────────────────

    def is_success_shown(self) -> bool:
        return self.is_displayed("success_msg")

    def get_success_text(self) -> str:
        return self.get_text("success_msg")

    def is_error_shown(self) -> bool:
        return self.is_displayed("error_msg")

    def get_error_text(self) -> str:
        return self.get_text("error_msg")

    def is_back_to_login_link_visible(self) -> bool:
        return self.is_displayed("back_to_login")
