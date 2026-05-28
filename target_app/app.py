"""
Target Web Application — Flask Server
Simulates a corporate portal with User Registration and Forgot Password functionality.
Supports ?break_locators=true URL parameter to simulate developer code changes
for the Self-Healing demo.
"""

import os
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "qa_demo_secret_key_2024"

# ── In-memory "database" for demo purposes ──────────────────────────────────
REGISTERED_USERS = {"test@example.com", "existing@demo.com", "admin@portal.com"}
BREAK_LOCATORS_STATE = {"active": False}


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    broken = BREAK_LOCATORS_STATE["active"]
    return render_template("portal.html", break_locators=broken)


@app.route("/register")
def register():
    broken = BREAK_LOCATORS_STATE["active"]
    return render_template("registration.html", break_locators=broken)


@app.route("/forgot-password")
def forgot_password():
    broken = BREAK_LOCATORS_STATE["active"]
    return render_template("forgot_password.html", break_locators=broken)


@app.route("/register/submit", methods=["POST"])
def register_submit():
    data = request.get_json() or request.form.to_dict()
    errors = []

    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    confirm_password = str(data.get("confirm_password", ""))
    terms = data.get("terms", False)

    if not first_name:
        errors.append("First name is required.")
    if not last_name:
        errors.append("Last name is required.")
    if not email or "@" not in email or "." not in email:
        errors.append("A valid email address is required.")
    if email in REGISTERED_USERS:
        errors.append("An account with this email already exists.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number.")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    if not terms:
        errors.append("You must accept the Terms and Conditions.")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    REGISTERED_USERS.add(email)
    return jsonify({
        "success": True,
        "message": f"Registration successful! Welcome, {first_name}. Please check your email for confirmation.",
        "redirect": "/register/success"
    })


@app.route("/register/success")
def register_success():
    return render_template("portal.html", success_message="Registration successful! Your account has been created.")


@app.route("/forgot-password/submit", methods=["POST"])
def forgot_password_submit():
    data = request.get_json() or request.form.to_dict()
    email = str(data.get("email", "")).strip().lower()

    if not email:
        return jsonify({"success": False, "errors": ["Email address is required."]}), 400
    if "@" not in email or "." not in email:
        return jsonify({"success": False, "errors": ["Please enter a valid email address."]}), 400

    # Return generic message regardless of whether email exists (security best practice)
    return jsonify({
        "success": True,
        "message": "If that email address is registered, you will receive a password reset link shortly."
    })


# ── Self-Healing Demo Control APIs ───────────────────────────────────────────

@app.route("/api/break-locators", methods=["POST"])
def break_locators():
    data = request.get_json() or {}
    state = data.get("active", not BREAK_LOCATORS_STATE["active"])
    BREAK_LOCATORS_STATE["active"] = bool(state)
    return jsonify({
        "success": True,
        "break_locators_active": BREAK_LOCATORS_STATE["active"],
        "message": f"Locator breakage {'ENABLED' if BREAK_LOCATORS_STATE['active'] else 'DISABLED'}. "
                   f"{'Element IDs have been changed to simulate developer code change.' if BREAK_LOCATORS_STATE['active'] else 'Element IDs restored to originals.'}"
    })


@app.route("/api/locator-status", methods=["GET"])
def locator_status():
    return jsonify({
        "break_locators_active": BREAK_LOCATORS_STATE["active"]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    print(f"\n{'='*50}")
    print(f"  [WEB] Target Portal running at: http://localhost:{port}")
    print(f"  [FORM] Registration: http://localhost:{port}/register")
    print(f"  [KEY] Forgot Password: http://localhost:{port}/forgot-password")
    print(f"  [API] Break Locators API: POST http://localhost:{port}/api/break-locators")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
