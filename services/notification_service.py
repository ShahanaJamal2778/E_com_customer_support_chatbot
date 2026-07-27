"""
services/notification_service.py

Sends escalation emails to the site admin when the chatbot can't
resolve something itself (fallback, complaints, refund/warranty
issues, feedback, etc.). Uses plain smtplib - no external email
provider SDK needed.

Configuration (add to .env):
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your_sending_gmail@gmail.com
    SMTP_PASSWORD=your_16_char_app_password      <- NOT your normal Gmail password
    ADMIN_EMAIL=shahmanjamal9@gmail.com
    FROM_EMAIL=your_sending_gmail@gmail.com

Gmail blocks plain-password SMTP login. You must create an "App
Password" for the sending account: Google Account -> Security ->
2-Step Verification (must be on) -> App passwords -> generate one for
"Mail", and use that 16-character value as SMTP_PASSWORD.

If SMTP isn't configured, notify_admin() logs a warning and returns a
failed envelope instead of raising - a missing email configuration
should never break the chat response the user is waiting on.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from services.utils import ok, fail

load_dotenv()  # don't rely on another module's import order to have loaded .env already

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "shahmanjamal9@gmail.com")


def notify_admin(subject: str, body: str) -> dict:
    """
    Send an escalation email to ADMIN_EMAIL. Best-effort: returns a
    `fail()` envelope (not an exception) if SMTP isn't configured or
    sending fails, so callers can swallow it without special-casing.
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return fail("Email not sent - SMTP_USERNAME/SMTP_PASSWORD are not configured in .env.")

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [ADMIN_EMAIL], msg.as_string())
        return ok(message="Escalation email sent to admin.")
    except Exception as exc:  # pragma: no cover - network/auth failure
        return fail(f"Failed to send escalation email: {exc}")


def notify_customer_query(user_id: str | None, intent: str, message: str) -> dict:
    """
    Convenience wrapper used by chatbot/actions.py: formats a
    customer's unresolved or complaint-flagged message into an email
    to the admin.
    """
    subject = f"Jamal Cart — customer needs help ({intent})"
    body = (
        f"Intent: {intent}\n"
        f"User ID: {user_id or 'guest (not logged in)'}\n\n"
        f"Message:\n{message}\n\n"
        "— Sent automatically by the Jamal Cart chatbot escalation flow."
    )
    return notify_admin(subject, body)