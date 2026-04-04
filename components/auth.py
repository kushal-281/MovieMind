import streamlit as st
import json
from cookies import cookies

# ---------------- RESTORE SESSION ----------------
def restore_session():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        if "user" in cookies:
            try:
                st.session_state.user = json.loads(cookies["user"])
            except:
                st.session_state.user = None

# ---------------- REQUIRE LOGIN ----------------
def require_login():
    restore_session()

    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("pages/login.py")

# ---------------- LOGIN USER ----------------
def login_user(user_dict):
    st.session_state.user = user_dict
    cookies["user"] = json.dumps(user_dict)
    cookies.save()