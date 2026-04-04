import streamlit as st
from sqlalchemy import text
from config.database import engine
import base64
import random
import re

st.set_page_config(layout="wide")

# ---------------- LOAD LOGO ----------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo = get_base64_image("assets/movieMind.png")

# ---------------- CAPTCHA INIT ----------------
if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 9)
    st.session_state.captcha_b = random.randint(1, 9)

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

        captcha_answer = st.text_input(
            f"What is {st.session_state.captcha_a} + {st.session_state.captcha_b} ?",
            key="captcha_input"
        )

        # ---------------- SIGNUP BUTTON ----------------
        if st.button("Signup Now", key="signup_btn"):

            if not username or not email or not password:
                st.error("All fields are required!")

            elif len(username) < 3:
                st.error("Username must be at least 3 characters!")

            elif not re.match(r"^[A-Za-z0-9_]+$", username):
                st.error("Username can only contain letters, numbers, and underscore!")

            elif not re.match(r"^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$", email):
                st.error("Invalid email format!")

            elif len(password) < 6:
                st.error("Password must be at least 6 characters!")

            elif not any(char.isdigit() for char in password):
                st.error("Password must contain at least 1 number!")

            elif not any(char.isalpha() for char in password):
                st.error("Password must contain at least 1 letter!")

            else:
                correct_answer = st.session_state.captcha_a + st.session_state.captcha_b

                if not captcha_answer.isdigit() or int(captcha_answer) != correct_answer:
                    st.error("Captcha verification failed!")

                else:
                    query = text("""
                    INSERT INTO users (username,email,password,role)
                    VALUES (:username,:email,:password,'user')
                    """)

                    try:
                        with engine.connect() as conn:
                            conn.execute(query, {
                                "username": username,
                                "email": email,
                                "password": password
                            })

                        st.success("Account created successfully!")

                        # Reset captcha
                        st.session_state.captcha_a = random.randint(1, 9)
                        st.session_state.captcha_b = random.randint(1, 9)

                        if st.button("Go to Login", key="goto_login_btn"):
                            st.switch_page("pages/login.py")

                    except:
                        st.error("Email already exists or database error.")