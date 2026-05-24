import streamlit as st
from sqlalchemy import text

from components.email_utils import is_valid_email
from components.footer import show_footer
from components.header import show_header
from components.static_page_styles import apply_static_page_styles
from components.theme import init_theme
from config.database import engine, ensure_schema


def _user_email(user: dict) -> str:
    if not user:
        return ""
    email = (user.get("email") or "").strip()
    if email:
        return email
    uid = user.get("user_id")
    if not uid:
        return ""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT email FROM users WHERE user_id = :uid LIMIT 1"),
                {"uid": int(uid)},
            ).fetchone()
        return (row[0] or "").strip() if row else ""
    except Exception:
        return ""

st.set_page_config(page_title="Contact Us - MovieMind", layout="wide")
init_theme()
ensure_schema()
show_header()
apply_static_page_styles()

st.title("Contact MovieMind")
st.caption("Have feedback, bug reports, or feature ideas? Send us a message.")

user = st.session_state.get("user") or {}
default_name = user.get("username", "")
default_email = _user_email(user)

with st.form("contact_form"):
    name = st.text_input("Your name", value=default_name)
    email = st.text_input("Your email", value=default_email)
    subject = st.text_input("Subject")
    message = st.text_area("Message", height=180)
    submitted = st.form_submit_button("Submit")

if submitted:
    missing = [
        label
        for label, value in (
            ("name", name),
            ("email", email),
            ("subject", subject),
            ("message", message),
        )
        if not (value or "").strip()
    ]
    if missing:
        st.error(f"Please fill all required fields: {', '.join(missing)}.")
    elif not is_valid_email(email.strip()):
        st.error("Please enter a valid email address.")
    else:
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO contact_messages (user_id, name, email, subject, message)
                        VALUES (:uid, :name, :email, :subject, :message)
                        """
                    ),
                    {
                        "uid": int(user["user_id"]) if user and user.get("user_id") else None,
                        "name": name.strip()[:100],
                        "email": email.strip()[:180],
                        "subject": subject.strip()[:200],
                        "message": message.strip(),
                    },
                )
            st.success("Thanks! Your message has been submitted successfully.")
        except Exception as e:
            st.error(f"Could not submit your message right now: {e}")



show_footer()