import base64

import streamlit as st
from sqlalchemy import text

from components.auth import login_user
from components.email_utils import is_valid_email
from components.theme import apply_theme_css, auth_page_styles, init_theme
from config.database import engine

st.set_page_config(layout="wide")
init_theme()
apply_theme_css()
auth_page_styles()


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


col1, col2, col3 = st.columns([2, 3, 2])

with col2:
    with st.container(border=True):
        st.markdown("### Login to MovieMind")
        st.caption("Discover films tailored to your taste.")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn", use_container_width=True):
            query = text(
                "SELECT * FROM users WHERE email=:email AND password=:password"
            )
            with engine.connect() as conn:
                user = conn.execute(
                    query, {"email": email, "password": password}
                ).fetchone()

            if user:
                login_user(
                    {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    }
                )
                st.success("Login successful!")
                st.switch_page("app.py")
            else:
                st.error("Invalid email or password.")

        if st.button("Forgot Password?", key="forgot_password_btn", use_container_width=True):
            if email and not is_valid_email(email):
                st.error("Please enter a valid email before continuing.")
            else:
                if email:
                    st.session_state["reset_email_prefill"] = email.strip()
                st.switch_page("pages/forgot_password.py")

        st.markdown(
            "<p style='text-align:center; margin-top:1rem;'>Don't have an account?</p>",
            unsafe_allow_html=True,
        )

        if st.button("Create account", key="signup_btn", use_container_width=True):
            st.switch_page("pages/signup.py")
