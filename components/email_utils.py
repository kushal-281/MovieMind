import os
import random
import re
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText


EMAIL_REGEX = re.compile(
    r"^(?![.])[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@"
    r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
)


def _load_env_file():
    # Basic .env loader (no external library required).
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Do not break auth flow if .env parsing fails.
        pass


def is_valid_email(email: str) -> bool:
    value = (email or "").strip()
    if not value or " " in value:
        return False
    return bool(EMAIL_REGEX.match(value))


def is_strong_password(password: str) -> tuple[bool, str]:
    p = password or ""
    if len(p) < 8:
        return False, "Password must be at least 8 characters."
    if not any(ch.isdigit() for ch in p):
        return False, "Password must contain at least 1 number."
    if not any(not ch.isalnum() for ch in p):
        return False, "Password must contain at least 1 special character."
    return True, ""


def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


def otp_expiry(minutes: int = 10) -> datetime:
    return datetime.now() + timedelta(minutes=minutes)


def send_plain_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    _load_env_file()
    # Gmail defaults are used so OTP email works with minimum setup.
    # Keep password in env var (never hardcode app password in code).
    host = os.getenv("MOVIEMIND_SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("MOVIEMIND_SMTP_PORT", "587"))
    sender = os.getenv("MOVIEMIND_SMTP_USER", "kushal9416@gmail.com")
    password = os.getenv("MOVIEMIND_SMTP_PASS")
    if not password:
        return False, "Set MOVIEMIND_SMTP_PASS to your Gmail app password."
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [to_email], msg.as_string())
        return True, "Email sent."
    except Exception as e:
        return False, str(e)


def send_otp_email(to_email: str, otp_code: str, purpose: str) -> tuple[bool, str]:
    subject = f"MovieMind OTP for {purpose}"
    body = (
        f"Hello,\n\n"
        f"Your MovieMind OTP for {purpose} is: {otp_code}\n"
        f"It is valid for 10 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"- MovieMind Team"
    )
    return send_plain_email(to_email, subject, body)
