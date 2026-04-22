import base64
import streamlit as st
from sqlalchemy import text

from components.auth import restore_session, track_site_time
from components.theme import apply_theme_css
from config.database import engine

# ---------------- SESSION DEFAULTS ----------------
if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

if "search_input" not in st.session_state:
    st.session_state.search_input = ""


# ---------------- LOAD IMAGE ----------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


# ---------------- HEADER ----------------
def header_without_search():
    restore_session()
    track_site_time()
    apply_theme_css()

    logo = get_base64_image("assets/movieMind.png")

    st.markdown(
        """
    <style>
    header {visibility:hidden;}
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}

    .block-container {
        padding-top: 0.5rem !important;
        max-width: 1350px;
        margin-top:0px; 
    }

    .mm-header-logo img {
        display: block;
        margin: 6px 0 4px 0;
        border-radius: 4px;
    }

    .mm-header-bar .stButton > button {
        border-radius: 8px;
        padding: 0.35rem 0.75rem;
        font-weight: 500;
        margin-top: 8px;
        margin-bottom: 8px; /* Change this if you want more/less button gap */
    }

    .mm-header-bar .stButton > button:hover {
        filter: brightness(0.98);
    }

    .mm-user-pill {
        margin-top: 14px;
        margin-left: 8px;
        padding: 6px 10px;
        background: #f4f4f5;
        border-radius: 999px;
        font-size: 0.95rem;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        font-weight: 600;
        letter-spacing: 0.2px;
        display: inline-block;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    u = st.session_state.get("user")
    is_admin = bool(u and u.get("role") == "admin")

    # ---------------- TOP ROW ----------------
    c_logo, c_user, c_prof, c_admin = st.columns([4.2, 2.2, 1.1, 1.1])

    with c_logo:
        st.markdown(
            f"""
            <div class="mm-header-logo">
                <a href="/" target="_self" title="MovieMind Home">
                    <img src="data:image/png;base64,{logo}" height="44" alt="MovieMind"/>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_user:
        if u:
            st.markdown(
                f'<div class="mm-user-pill">👤 {u["username"]}</div>',
                unsafe_allow_html=True,
            )

    with c_prof:
        if u:
            if st.button("Profile", key="profile_btn", use_container_width=True):
                if is_admin:
                    st.switch_page("pages/admin_profile.py")
                else:
                    st.switch_page("pages/profile.py")

    with c_admin:
        if is_admin:
            if st.button("Admin", key="admin_panel_btn", use_container_width=True):
                st.switch_page("pages/admin_auth.py")
        elif not u:
            if st.button("Login", key="login_btn", use_container_width=True):
                st.switch_page("pages/login.py")

    # ---------------- SEARCH BAR REMOVED ----------------
    # (Previously search input + button + DB insert was here)

    st.divider()