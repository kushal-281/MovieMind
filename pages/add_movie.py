"""Redirect legacy add-movie page to profile."""

import streamlit as st

from components.auth import restore_session

st.set_page_config(layout="wide")
restore_session()

if not st.session_state.get("user"):
    st.switch_page("pages/login.py")

st.switch_page("pages/profile.py")
