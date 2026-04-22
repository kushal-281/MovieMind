import streamlit as st
from sqlalchemy import text

from components.footer import show_footer
from components.header_without_search import header_without_search
from config.database import engine, ensure_schema

st.set_page_config(page_title="Contact Us - MovieMind", layout="wide")
ensure_schema()
header_without_search()

st.title("Contact MovieMind")
st.caption("Have feedback, bug reports, or feature ideas? Send us a message.")

user = st.session_state.get("user") or {}
default_name = user.get("username", "")

with st.form("contact_form", clear_on_submit=True):
    name = st.text_input("Your name", value=default_name)
    email = st.text_input("Your email")
    subject = st.text_input("Subject")
    message = st.text_area("Message", height=180)
    submitted = st.form_submit_button("Submit")

if submitted:
    if not name.strip() or not email.strip() or not message.strip():
        st.error("Please fill name, email and message.")
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

st.markdown("---")
st.write("Email: support@moviemind.com")
st.write("Location: Sonipat, Haryana, India")

show_footer()