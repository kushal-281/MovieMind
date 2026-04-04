import streamlit as st
import json
from components.footer import show_footer
from cookies import cookies
from components.header import show_header

st.set_page_config(layout="wide")

# ---------------- GLOBAL WIDTH FIX ----------------
st.markdown("""
<style>
.block-container {
    max-width: 1350px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DEFAULT SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- SESSION FLAG ----------------
if "session_loaded" not in st.session_state:
    st.session_state.session_loaded = False

# ---------------- FORCE LOGOUT CHECK ----------------
if "force_logout" in st.session_state:
    st.session_state.user = None

# ---------------- RESTORE SESSION ----------------
if (
    st.session_state.user is None
    and "force_logout" not in st.session_state
    and st.session_state.session_loaded
):
    if cookies.get("user"):
        try:
            st.session_state.user = json.loads(cookies.get("user"))
        except:
            st.session_state.user = None

# ---------------- MARK SESSION LOADED ----------------
st.session_state.session_loaded = True

# ---------------- HEADER ----------------
show_header()

# ---------------- MAIN CONTENT ----------------
st.title("🎬 MovieMind Dashboard")

if st.session_state.user:
    st.success(f"Welcome, {st.session_state.user['username']}")

    if st.session_state.user.get("role") == "admin":
        st.info("You are logged in as Admin")
    else:
        st.info("You are logged in as User")

else:
    st.info("Please login to access full features")

# ---------------- FOOTER ----------------
show_footer()