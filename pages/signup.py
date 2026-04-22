import streamlit as st
from sqlalchemy import text
from config.database import engine
from config.database import ensure_schema
import base64
import random
import re
from datetime import datetime

from components.email_utils import (
    generate_otp,
    is_strong_password,
    is_valid_email,
    otp_expiry,
    send_otp_email,
)
from components.theme import apply_theme_css

st.set_page_config(layout="wide")
apply_theme_css()

# ---------------- LOAD LOGO ----------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo = get_base64_image("assets/movieMind.png")
ensure_schema()


def password_strength_label(password: str):
    checks = {
        "length": len(password) >= 8,
        "digit": any(char.isdigit() for char in password),
        "special": any(not char.isalnum() for char in password),
        "alpha": any(char.isalpha() for char in password),
    }
    score = sum(checks.values())
    if score == 4:
        return "Strong", "green"
    return "Weak", "red"

# ---------------- CAPTCHA INIT ----------------
if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 9)
    st.session_state.captcha_b = random.randint(1, 9)
if "signup_pending" not in st.session_state:
    st.session_state.signup_pending = None

# ---------------- GLOBAL STYLE ----------------
st.markdown("""
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

/* Buttons */
div.stButton > button {
    background-color: #007BFF;
    color: white;
    border-radius: 6px;
    width: 100%;
    margin-top: 10px;
    transition: 0.3s;
}

/* Hover */
div.stButton > button:hover {
    background-color: #0056b3;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([6,1])

with col1:
    st.markdown(
        f"""
        <a href="/" target="_self">
            <img src="data:image/png;base64,{logo}" height="45" style="cursor:pointer;">
        </a>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------------- CENTER SIGNUP CARD ----------------
col1, col2, col3 = st.columns([2,3,2])

with col2:
    with st.container(border=True):

        st.markdown("### 📝 Signup")
        st.markdown("<p style='color:gray;'>Create your MovieMind account</p>", unsafe_allow_html=True)

        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if password:
            strength_text, strength_color = password_strength_label(password)
            st.markdown(
                f"<p style='margin:0;color:{strength_color};font-weight:600;'>Password Strength: {strength_text}</p>",
                unsafe_allow_html=True,
            )

        captcha_answer = st.text_input(
            f"What is {st.session_state.captcha_a} + {st.session_state.captcha_b} ?",
            key="captcha_input"
        )
        otp_input = st.text_input("Enter OTP (after sending)", key="signup_otp_input")

        # ---------------- SEND OTP BUTTON ----------------
        if st.button("Send OTP", key="signup_send_otp_btn"):

            if not username or not email or not password:
                st.error("All fields are required!")

            elif len(username) < 3:
                st.error("Username must be at least 3 characters!")

            elif not re.match(r"^[A-Za-z0-9_]+$", username):
                st.error("Username can only contain letters, numbers, and underscore!")

            elif not is_valid_email(email):
                st.error("Invalid email format!")

            else:
                ok_pw, pw_msg = is_strong_password(password)
                if not ok_pw:
                    st.error(pw_msg)
                    st.stop()

                correct_answer = st.session_state.captcha_a + st.session_state.captcha_b

                if not captcha_answer.isdigit() or int(captcha_answer) != correct_answer:
                    st.error("Captcha verification failed!")

                else:
                    exists_query = text(
                        """
                        SELECT user_id
                        FROM users
                        WHERE username = :username OR email = :email
                        LIMIT 1
                        """
                    )
                    query = text("""
                    INSERT INTO users (username,email,password,role)
                    VALUES (:username,:email,:password,'user')
                    """)

                    try:
                        with engine.begin() as conn:
                            existing = conn.execute(
                                exists_query,
                                {"username": username.strip(), "email": email.strip()},
                            ).fetchone()
                            if existing:
                                st.error("Username or email already exists.")
                                st.stop()
                    except Exception:
                        st.error("Could not validate account uniqueness. Try again.")
                        st.stop()

                    otp_code = generate_otp()
                    ok_mail, detail = send_otp_email(email.strip(), otp_code, "signup verification")
                    if not ok_mail:
                        st.error(f"OTP email failed: {detail}")
                        st.stop()
                    st.session_state.signup_pending = {
                        "username": username.strip(),
                        "email": email.strip(),
                        "password": password,
                        "otp": otp_code,
                        "expires_at": otp_expiry().isoformat(),
                    }
                    st.success("OTP sent to your email. Enter it below and click Create Account.")

        # ---------------- VERIFY OTP + CREATE ACCOUNT ----------------
        if st.button("Verify OTP & Create Account", key="signup_verify_btn"):
            pending = st.session_state.get("signup_pending")
            if not pending:
                st.error("Please click Send OTP first.")
            elif not otp_input.strip():
                st.error("Please enter OTP.")
            elif datetime.now() > datetime.fromisoformat(pending["expires_at"]):
                st.error("OTP expired. Please request a new OTP.")
                st.session_state.signup_pending = None
            elif otp_input.strip() != pending["otp"]:
                st.error("Invalid OTP.")
            else:
                query = text("""
                INSERT INTO users (username,email,password,role)
                VALUES (:username,:email,:password,'user')
                """)
                try:
                    with engine.begin() as conn:
                        conn.execute(query, {
                            "username": pending["username"],
                            "email": pending["email"],
                            "password": pending["password"],
                        })
                    st.success("Account created successfully! Please login.")
                    st.session_state.signup_pending = None
                    st.session_state.captcha_a = random.randint(1, 9)
                    st.session_state.captcha_b = random.randint(1, 9)
                except Exception:
                    st.error("Email/username may already exist or database error.")

        if st.button("Go to Login", key="goto_login_btn"):
            st.switch_page("pages/login.py")