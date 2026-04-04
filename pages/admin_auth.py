import streamlit as st
from components.header import show_header
from components.auth import require_login

st.set_page_config(layout="wide")

require_login()

# ROLE CHECK
if st.session_state.user.get("role") != "admin":
    st.error("Access Denied")
    st.stop()

show_header()

st.title("Admin Panel")