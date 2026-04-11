import streamlit as st
from sqlalchemy import text

from admin.dashboard import show_admin_dashboard
from components.auth import restore_session
from components.header import show_header
from cookies import cookies
from config.database import engine

st.set_page_config(layout="wide")

restore_session()

user = st.session_state.get("user")
if not user or user.get("role") != "admin":
    st.switch_page("app.py")

show_header()

st.title("🛡️ Admin account")

c1, c2 = st.columns([1, 2])
with c1:
    st.write(f"**Username:** {user['username']}")
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT email, COALESCE(total_site_seconds,0) FROM users WHERE user_id = :uid"
                ),
                {"uid": int(user["user_id"])},
            ).fetchone()
        if row:
            st.write(f"**Email:** {row[0]}")
            ts = int(row[1] or 0)
            st.write(f"**Your time on site:** {ts // 3600}h {(ts % 3600) // 60}m")
    except Exception:
        pass

    if st.button("Logout", key="admin_logout_btn"):
        st.session_state["force_logout"] = True
        if cookies.get("user"):
            cookies.pop("user", None)
            cookies.save()
        for k in list(st.session_state.keys()):
            if k != "force_logout":
                del st.session_state[k]
        st.switch_page("app.py")

with c2:
    st.info(
        "This is the **admin profile**. Regular users use the standard Profile page. "
        "Below is the full admin panel with all user activity."
    )

st.divider()
show_admin_dashboard()
