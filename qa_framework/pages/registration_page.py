"""
RegistrationPage — Page Object for the User Registration form.
All element interactions go through BasePage's self-healing find().
"""

from qa_framework.pages.base_page import BasePage


class RegistrationPage(BasePage):
    """
    Page Object Model for /register page.
    Encapsulates all locators and actions for the registration form.
    """

    PAGE_NAME = "registration"
    PATH = "/register"

    def __init__(self, driver):
        super().__init__(driver, self.PAGE_NAME)

    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self):
        """Navigate to the registration page."""
        self.navigate_to(self.PATH)
        return self

    # ── Page Actions ──────────────────────────────────────────────────────────

    def enter_first_name(self, name: str):
        self.clear_and_type("first_name", name)
        return self

    def enter_last_name(self, name: str):
        self.clear_and_type("last_name", name)
        return self

    def enter_email(self, email: str):
        self.clear_and_type("email", email)
        return self

    def enter_password(self, password: str):
        self.clear_and_type("password", password)
        return self

    def enter_confirm_password(self, password: str):
        self.clear_and_type("confirm_password", password)
        return self

    def accept_terms(self):
        element = self.find("terms")
        if not element.is_selected():
            element.click()
        return self

    def click_register(self):
        self.safe_click("register_btn")
        return self

    # ── Composite Actions ─────────────────────────────────────────────────────

    def register(self, first_name: str, last_name: str, email: str,
                 password: str, confirm_password: str = None,
                 accept_terms: bool = True):
        """
        Fill and submit the complete registration form.

        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
            password: Chosen password
            confirm_password: Confirmation password (defaults to same as password)
            accept_terms: Whether to check the T&C checkbox
        """
        confirm = confirm_password if confirm_password is not None else password
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm_password(confirm)
        if accept_terms:
            self.accept_terms()
        self.click_register()
        return self

    # ── Assertions / State Checks ─────────────────────────────────────────────

    def is_success_shown(self) -> bool:
        """Check if the success message is visible after submission."""
        return self.is_displayed("form_success")

    def get_success_text(self) -> str:
        """Get the success message text."""
        return self.get_text("form_success")

    def is_error_shown(self) -> bool:
        """Check if the error container is visible."""
        return self.is_displayed("form_error")

    def get_error_text(self) -> str:
        """Get the error message text."""
        return self.get_text("form_error")

    def get_page_title(self) -> str:
        return self.driver.title
