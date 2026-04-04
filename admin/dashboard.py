import streamlit as st
from config.database import engine
from sqlalchemy import text

def show_admin_dashboard():

    if not st.session_state.user or st.session_state.user["role"] != "admin":
        st.error("Unauthorized Access")
        return

    st.title("Admin Dashboard")

    st.subheader("All Users")

    with engine.connect() as conn:
        users = conn.execute(text("SELECT username, email, role FROM users")).fetchall()

    for u in users:
        st.write(u)

    st.subheader("Search History")

    with engine.connect() as conn:
        history = conn.execute(text("SELECT * FROM search_history")).fetchall()

    for h in history:
        st.write(h)