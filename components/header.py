import base64

import streamlit as st
from sqlalchemy import text

from components.auth import restore_session, track_site_time
from components.theme import apply_theme_css
from config.database import engine

if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

if "search_input" not in st.session_state:
    st.session_state.search_input = ""


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def show_header():
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
        color: #000;
    }

    div[data-testid="stHorizontalBlock"]:has(.mm-search-row) [data-testid="column"] {
        vertical-align: middle;
    }

    .mm-search-row [data-testid="stTextInput"] label {
        display: none;
    }
    .mm-search-row [data-testid="stTextInput"] input {
        margin-top: 6px !important;
        border-radius: 8px !important;
    }
    .mm-search-row .stButton > button {
        margin-top: 16px !important;
        margin-bottom: 8px !important; /* Keep spacing editable from one place */
        border-radius: 8px !important;
        min-height: 42px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    u = st.session_state.get("user")
    is_admin = bool(u and u.get("role") == "admin")

    # Top row: logo / home, user, profile, admin (if admin)
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

    st.markdown('<div class="mm-header-bar">', unsafe_allow_html=True)
    sc1, sc2 = st.columns([6, 1], gap="small")

    with sc1:
        st.markdown('<div class="mm-search-row">', unsafe_allow_html=True)
        st.text_input("", placeholder="Search movies, actors, genres…", key="search_input")
        st.markdown("</div>", unsafe_allow_html=True)
        q_preview = st.session_state.get("search_input", "").strip()
        if len(q_preview) >= 2:
            try:
                with engine.connect() as conn:
                    s_df = conn.execute(
                        text(
                            """
                            SELECT DISTINCT title
                            FROM movies
                            WHERE title LIKE :q
                            ORDER BY popularity DESC
                            LIMIT 8
                            """
                        ),
                        {"q": f"{q_preview}%"},
                    ).fetchall()
                titles = [r[0] for r in s_df if r and r[0]]
                if titles:
                    st.caption("Suggestions")
                    sug_cols = st.columns(4)
                    for idx, t in enumerate(titles):
                        with sug_cols[idx % 4]:
                            if st.button(str(t), key=f"sugg_{idx}", use_container_width=True):
                                st.session_state.search_input = str(t)
                                st.session_state.search_movie = str(t)
                                st.switch_page("pages/search.py")
            except Exception:
                pass

    with sc2:
        if st.button("Search", key="search_btn", use_container_width=True):
            if st.session_state.search_input.strip():
                st.session_state.search_movie = st.session_state.search_input
                q = st.session_state.search_input.strip()
                u2 = st.session_state.get("user")
                if u2 and u2.get("user_id"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    "INSERT INTO search_history (user_id, query) VALUES (:uid, :q)"
                                ),
                                {"uid": int(u2["user_id"]), "q": q[:255]},
                            )
                    except Exception:
                        pass
                st.switch_page("pages/search.py")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # # Quick links to browse pages
    # n1, n2, n3, n4 = st.columns(4)
    # with n1:
    #     if st.button("By Year", key="nav_year", use_container_width=True):
    #         st.switch_page("pages/year.py")
    # with n2:
    #     if st.button("By Industry", key="nav_industry", use_container_width=True):
    #         st.switch_page("pages/industry.py")
    # with n3:
    #     if st.button("By Genre", key="nav_genre", use_container_width=True):
    #         st.switch_page("pages/genre.py")
    # with n4:
    #     if st.button("Home", key="nav_home", use_container_width=True):
    #         st.switch_page("app.py")

    # st.divider()
