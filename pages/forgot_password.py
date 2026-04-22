import base64
from datetime import datetime

import streamlit as st
from sqlalchemy import text

from components.email_utils import (
    generate_otp,
    is_strong_password,
    is_valid_email,
    otp_expiry,
    send_otp_email,
)
from components.theme import apply_theme_css
from config.database import engine

st.set_page_config(layout="wide")
apply_theme_css()


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


logo = get_base64_image("assets/movieMind.png")
if "forgot_pending" not in st.session_state:
    st.session_state.forgot_pending = None

st.markdown(
    """
<style>
header {visibility:hidden;}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
.block-container {
    max-width: 1250px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 0rem !important;
}
div.stButton > button {
    background-color: #007BFF;
    color: white;
    border-radius: 6px;
    width: 100%;
    margin-top: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

col1, _ = st.columns([6, 1])
with col1:
    st.markdown(
        f"""
        <a href="/" target="_self">
            <img src="data:image/png;base64,{logo}" height="45" style="cursor:pointer;">
        </a>
        """,
        unsafe_allow_html=True,
    )
st.divider()

c1, c2, c3 = st.columns([2, 3, 2])
with c2:
    with st.container(border=True):
        st.markdown("### 🔑 Forgot Password")
        st.caption("Enter your email, verify OTP, then set a new password.")

        prefill_email = st.session_state.get("reset_email_prefill", "")
        email = st.text_input("Email", value=prefill_email, key="forgot_email")
        otp_input = st.text_input("OTP", key="forgot_otp")
        new_password = st.text_input("New Password", type="password", key="forgot_new_password")
        confirm_password = st.text_input(
            "Confirm New Password", type="password", key="forgot_confirm_password"
        )

        if st.button("Send OTP", key="forgot_send_otp"):
            if not is_valid_email(email):
                st.error("Invalid email format.")
                st.stop()
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT user_id FROM users WHERE email = :email LIMIT 1"),
                    {"email": email.strip()},
                ).fetchone()
            if not row:
                st.error("No account found with this email.")
                st.stop()

            otp_code = generate_otp()
            ok, detail = send_otp_email(email.strip(), otp_code, "password reset")
            if not ok:
                st.error(f"OTP email failed: {detail}")
                st.stop()
            st.session_state.forgot_pending = {
                "email": email.strip(),
                "otp": otp_code,
                "expires_at": otp_expiry().isoformat(),
            }
            st.success("OTP sent to your email.")

        if st.button("Verify OTP & Update Password", key="forgot_update_password"):
            pending = st.session_state.get("forgot_pending")
            if not pending:
                st.error("Please send OTP first.")
            elif pending["email"] != email.strip():
                st.error("Use the same email you used for OTP.")
            elif not otp_input.strip():
                st.error("Please enter OTP.")
            elif datetime.now() > datetime.fromisoformat(pending["expires_at"]):
                st.error("OTP expired. Request a new OTP.")
                st.session_state.forgot_pending = None
            elif otp_input.strip() != pending["otp"]:
                st.error("Invalid OTP.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok_pw, pw_msg = is_strong_password(new_password)
                if not ok_pw:
                    st.error(pw_msg)
                    st.stop()
                with engine.begin() as conn:
                    conn.execute(
                        text("UPDATE users SET password = :password WHERE email = :email"),
                        {"password": new_password, "email": email.strip()},
                    )
                st.session_state.forgot_pending = None
                st.success("Password updated successfully. Please login.")

        if st.button("Back to Login", key="forgot_back_login"):
            st.switch_page("pages/login.py")
