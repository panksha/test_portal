"""
Test Suite: Forgot Password
TC-FP-001 to TC-FP-007

Covers: valid email submission, unregistered email (generic response),
empty email, invalid format, success message content, back-to-login link.
TC-FP-007: INTENTIONALLY FAILING — asserts a feature not yet implemented.
"""

import pytest
import time
from qa_framework.pages.forgot_password_page import ForgotPasswordPage


@pytest.fixture(autouse=True)
def fp_page(driver):
    """Open the forgot password page before each test."""
    page = ForgotPasswordPage(driver)
    page.open()
    time.sleep(0.5)
    return page


# ── TC-FP-001: Valid Registered Email ────────────────────────────────────────

def test_valid_email_submission(driver):
    """
    TC-FP-001 | Priority: High | Risk: High | AC: AC-001, AC-007
    Verify success message is shown for a valid, registered email.
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("test@example.com")
    time.sleep(3.0)
    assert page.is_success_shown(), \
        f"Expected success message for valid email. Error: {page.get_error_text() if page.is_error_shown() else 'None'}"
    msg = page.get_success_text()
    assert len(msg) > 0, "Success message text should not be empty."


# ── TC-FP-002: Unregistered Email — Generic Response (Security) ──────────────

def test_unregistered_email(driver):
    """
    TC-FP-002 | Priority: High | Risk: Medium | AC: AC-002
    Verify a generic response is given even for an unregistered email
    (to prevent user enumeration — security best practice).
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("notregistered99999@test.com")
    time.sleep(3.0)
    # Should still show a success/generic message — NOT a "user not found" error
    assert page.is_success_shown(), \
        "Expected generic success message even for unregistered email (security: no user enumeration)."
    msg = page.get_success_text().lower()
    # Should NOT reveal whether email exists
    assert "not found" not in msg and "does not exist" not in msg, \
        "Response reveals whether email is registered — security risk!"


# ── TC-FP-003: Empty Email Field ─────────────────────────────────────────────

def test_empty_email_field(driver):
    """
    TC-FP-003 | Priority: High | Risk: Medium | AC: AC-006
    Verify an error is shown when the email field is submitted empty.
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("")
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected validation error for empty email."
    error_text = page.get_error_text().lower()
    assert "email" in error_text or "required" in error_text, \
        f"Expected email required error. Got: '{error_text}'"


# ── TC-FP-004: Invalid Email Format ──────────────────────────────────────────

def test_invalid_email_format(driver):
    """
    TC-FP-004 | Priority: High | Risk: Medium | AC: AC-006
    Verify an error is shown for a malformed email address.
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("this-is-not-valid")
    time.sleep(3.0)
    assert page.is_error_shown(), "Expected error for invalid email format."
    error_text = page.get_error_text().lower()
    assert "valid" in error_text or "email" in error_text, \
        f"Expected email format error. Got: '{error_text}'"


# ── TC-FP-005: Success Message is Informative ─────────────────────────────────

def test_success_message_displayed(driver):
    """
    TC-FP-005 | Priority: Medium | Risk: Low | AC: AC-007
    Verify the success message tells the user what to do next.
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("test@example.com")
    time.sleep(3.0)
    assert page.is_success_shown(), "Expected success message to be visible."
    msg = page.get_success_text().lower()
    # Message should mention email/link/reset
    assert any(word in msg for word in ["email", "link", "reset", "sent", "receive"]), \
        f"Success message should reference email/link action. Got: '{msg}'"


# ── TC-FP-006: Back to Login Link Visible ────────────────────────────────────

def test_back_to_login_link(driver):
    """
    TC-FP-006 | Priority: Low | Risk: Low | AC: UI Navigation
    Verify the 'Back to Login' link is present and visible on the page.
    """
    page = ForgotPasswordPage(driver)
    page.open()
    time.sleep(3.0)
    assert page.is_back_to_login_link_visible(), \
        "Expected 'Back to Login' link to be visible on the forgot password page."


# ── TC-FP-007: [INTENTIONAL FAIL] Success Message Must Mention Link Expiry ──

def test_success_message_shows_link_expiry_time(driver):
    """
    TC-FP-007 | Priority: Medium | Risk: Medium | AC: AC-004 (Link Expiry)
    Status: EXPECTED TO FAIL (Missing UX Feature)

    WHY THIS FAILS:
      The current success message says:
        'If that email address is registered, you will receive a
         password reset link shortly.'

      It does NOT tell the user how long the reset link is valid for.
      Good security UX requires informing users of the expiry window
      (e.g., 'Your reset link will expire in 30 minutes') so they
      act promptly and understand why a link might stop working.

    WHAT NEEDS TO BE FIXED IN THE APP:
      target_app/app.py  → Update the success message to include:
        '...link will expire in 30 minutes.'

    Interview talking point:
      'This test acts as an executable UX requirement. Once the dev team
      updates the message, this test will automatically turn green —
      no manual regression check needed.'
    """
    page = ForgotPasswordPage(driver)
    page.open()
    page.submit_reset_request("test@example.com")
    time.sleep(3.0)

    assert page.is_success_shown(), "Success message should be visible after valid email."

    msg = page.get_success_text().lower()

    # ── This assertion WILL FAIL ─────────────────────────────────────────────
    # The current message has NO mention of expiry time (minutes / expire / valid).
    # Expected: message includes expiry info like '30 minutes' or 'expire'
    # Actual:   '...you will receive a password reset link shortly.'
    assert any(word in msg for word in ["minutes", "expire", "expires", "valid for", "30"]), (
        f"[BUG] Success message does not inform user how long the reset link is valid. "
        f"Actual message: '{msg}'. "
        f"Fix: Update /forgot-password/submit response to include: "
        f"'Your reset link will expire in 30 minutes.'"
    )
