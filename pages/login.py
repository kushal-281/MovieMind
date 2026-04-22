import streamlit as st
from sqlalchemy import text
from config.database import engine
import base64

from components.auth import login_user
from components.email_utils import is_valid_email
from components.theme import apply_theme_css

st.set_page_config(layout="wide")
apply_theme_css()

# ---------------- LOAD LOGO ----------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo = get_base64_image("assets/movieMind.png")

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
    margin-top: -10px !important;
}

/* Buttons */
div.stButton > button {
    background-color: #007BFF;
    color: white;
    border-radius: 6px;
    width: 100%;
    margin-top: 10px;
    transition: 0.3s;
    padding: 0 10px ;
}

/* Hover Effect */
div.stButton > button:hover {
    background-color: #0056b3;  /* Dark Blue */
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

# ---------------- CENTER LOGIN CARD ----------------
col1, col2, col3 = st.columns([2,3,2])

with col2:
    with st.container(border=True):

        st.markdown("### 🔐 Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        # LOGIN BUTTON
        if st.button("Login", key="login_btn"):

            query = text("SELECT * FROM users WHERE email=:email AND password=:password")

            with engine.connect() as conn:
                user = conn.execute(query, {
                    "email": email,
                    "password": password
                }).fetchone()

            if user:
                user_dict = {
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role
                }

                login_user(user_dict)

                st.success("Login Successful")
                st.switch_page("app.py")

            else:
                st.error("Invalid credentials")

        if st.button("Forgot Password?", key="forgot_password_btn"):
            if email and not is_valid_email(email):
                st.error("Please enter a valid email before continuing.")
            else:
                if email:
                    st.session_state["reset_email_prefill"] = email.strip()
                st.switch_page("pages/forgot_password.py")

        # SIGNUP TEXT
        st.markdown("<p style='text-align:center;'>Don't have an account?</p>", unsafe_allow_html=True)

        # SIGNUP BUTTON
        if st.button("Signup", key="signup_btn"):
            st.switch_page("pages/signup.py")