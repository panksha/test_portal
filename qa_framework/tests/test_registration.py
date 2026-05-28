"""
Test Suite: User Registration
TC-REG-001 to TC-REG-009

Covers: valid registration, missing fields, weak passwords,
duplicate email, password mismatch, invalid email, T&C not accepted.
TC-REG-009: INTENTIONALLY FAILING — asserts a feature not yet implemented.
"""

import pytest
import time
from qa_framework.pages.registration_page import RegistrationPage


BASE_EMAIL = "john.doe.autotest"
VALID_PASSWORD = "SecurePass@123"


@pytest.fixture(autouse=True)
def registration_page(driver):
    """Open the registration page before each test."""
    page = RegistrationPage(driver)
    page.open()
    # Small wait to ensure page is fully loaded
    time.sleep(0.5)
    return page


# ── TC-REG-001: Valid Registration ──────────────────────────────────────────

def test_valid_registration(driver):
    """
    TC-REG-001 | Priority: High | Risk: High | AC: AC-001, AC-006
    Verify a user can register with all valid inputs.
    """
    # Use unique email to avoid duplicate issues across test runs
    unique_email = f"{BASE_EMAIL}.{int(time.time())}@example.com"
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="John",
        last_name="Doe",
        email=unique_email,
        password=VALID_PASSWORD
    )
    time.sleep(3.0)
    assert page.is_success_shown(), \
        f"Expected success message after valid registration. Error: {page.get_error_text() if page.is_error_shown() else 'No error shown'}"
    success_text = page.get_success_text()
    assert "successful" in success_text.lower() or "Registration" in success_text, \
        f"Success message did not contain expected text. Got: '{success_text}'"


# ── TC-REG-002: Missing First Name ──────────────────────────────────────────

def test_missing_first_name(driver):
    """
    TC-REG-002 | Priority: High | Risk: Medium | AC: AC-004
    Verify registration fails when first name is omitted.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="",
        last_name="Doe",
        email="test.missing.fn@example.com",
        password=VALID_PASSWORD
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected validation error when first name is missing."
    error_text = page.get_error_text().lower()
    assert "first name" in error_text, \
        f"Expected 'first name' in error message. Got: '{error_text}'"


# ── TC-REG-003: Weak Password (No Special Character) ────────────────────────

def test_weak_password(driver):
    """
    TC-REG-003 | Priority: High | Risk: High | AC: AC-002
    Verify registration fails for a password without a special character.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="Jane",
        last_name="Smith",
        email="test.weak.pass@example.com",
        password="Password1"  # No special character
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error for password without special character."
    error_text = page.get_error_text().lower()
    assert "special" in error_text or "password" in error_text, \
        f"Expected password policy error. Got: '{error_text}'"


# ── TC-REG-004: Duplicate Email ──────────────────────────────────────────────

def test_duplicate_email(driver):
    """
    TC-REG-004 | Priority: High | Risk: High | AC: AC-003
    Verify registration fails when using an already-registered email.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="Test",
        last_name="User",
        email="existing@demo.com",  # Pre-seeded in target_app
        password=VALID_PASSWORD
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error for duplicate email."
    error_text = page.get_error_text().lower()
    assert "already" in error_text or "exists" in error_text or "email" in error_text, \
        f"Expected duplicate email error. Got: '{error_text}'"


# ── TC-REG-005: Missing Last Name ────────────────────────────────────────────

def test_missing_last_name(driver):
    """
    TC-REG-005 | Priority: Medium | Risk: Medium | AC: AC-004
    Verify registration fails when last name is omitted.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="John",
        last_name="",
        email="test.missing.ln@example.com",
        password=VALID_PASSWORD
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected validation error when last name is missing."
    error_text = page.get_error_text().lower()
    assert "last name" in error_text, \
        f"Expected 'last name' in error message. Got: '{error_text}'"


# ── TC-REG-006: Invalid Email Format ────────────────────────────────────────

def test_invalid_email_format(driver):
    """
    TC-REG-006 | Priority: High | Risk: Medium | AC: AC-004
    Verify registration fails for malformed email addresses.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="John",
        last_name="Doe",
        email="not-a-valid-email",
        password=VALID_PASSWORD
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error for invalid email format."
    error_text = page.get_error_text().lower()
    assert "email" in error_text or "valid" in error_text, \
        f"Expected email format error. Got: '{error_text}'"


# ── TC-REG-007: Terms Not Accepted ───────────────────────────────────────────

def test_terms_not_accepted(driver):
    """
    TC-REG-007 | Priority: High | Risk: Medium | AC: AC-005
    Verify registration fails when Terms & Conditions are not accepted.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="John",
        last_name="Doe",
        email=f"test.terms.{int(time.time())}@example.com",
        password=VALID_PASSWORD,
        accept_terms=False  # Don't check T&C
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error when T&C not accepted."
    error_text = page.get_error_text().lower()
    assert "terms" in error_text or "conditions" in error_text or "accept" in error_text, \
        f"Expected T&C error. Got: '{error_text}'"


# ── TC-REG-008: Password Mismatch ────────────────────────────────────────────

def test_password_mismatch(driver):
    """
    TC-REG-008 | Priority: High | Risk: High | AC: AC-002
    Verify registration fails when password and confirm password don't match.
    """
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="John",
        last_name="Doe",
        email=f"test.mismatch.{int(time.time())}@example.com",
        password=VALID_PASSWORD,
        confirm_password="DifferentPass@456"
    )
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error for mismatched passwords."
    error_text = page.get_error_text().lower()
    assert "match" in error_text or "password" in error_text, \
        f"Expected password mismatch error. Got: '{error_text}'"


# ── TC-REG-009: [INTENTIONAL FAIL] Redirect to Dashboard After Registration ──

def test_redirect_to_dashboard_after_registration(driver):
    """
    TC-REG-009 | Priority: High | Risk: High | AC: AC-006
    Status: EXPECTED TO FAIL (BUG / Missing Feature)

    WHY THIS FAILS:
      After a successful registration, the current app shows a success
      message on the SAME page. It does NOT redirect the user to a
      '/dashboard' URL.

      A real enterprise portal SHOULD redirect to a personalised dashboard
      after login. This test documents that gap — it acts as a living
      bug report inside the test suite.

    WHAT NEEDS TO BE FIXED IN THE APP:
      target_app/app.py  → /register/submit should return
                           redirect: '/dashboard' instead of staying on page.
      target_app/app.py  → Add a /dashboard route.

    Interview talking point:
      'Failing tests are not just failures — they are executable bug reports.
      TC-REG-009 tells every developer exactly what is missing and why.'
    """
    unique_email = f"redirect.test.{int(time.time())}@example.com"
    page = RegistrationPage(driver)
    page.open()
    page.register(
        first_name="Jane",
        last_name="Smith",
        email=unique_email,
        password=VALID_PASSWORD
    )
    time.sleep(3.0)

    current_url = page.get_current_url()

    # ── This assertion WILL FAIL ─────────────────────────────────────────────
    # The app stays on /register after success (no redirect implemented yet).
    # Expected: URL should contain '/dashboard'
    # Actual:   URL still contains '/register'
    assert "/dashboard" in current_url, (
        f"[BUG] After successful registration, user should be redirected to /dashboard. "
        f"Actual URL: '{current_url}'. "
        f"Fix: Add /dashboard route and return redirect URL from /register/submit."
    )
