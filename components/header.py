import base64
import html as html_lib

import streamlit as st
from sqlalchemy import text

from components.auth import restore_session, track_site_time
from components.theme import apply_theme_css, init_theme
from config.database import engine

SK_SEARCH_MOVIE = "search_movie"
SK_SEARCH_INPUT = "search_input"
SK_SEARCH_PENDING = "search_movie_pending"


def _ensure_search_state():
    if SK_SEARCH_MOVIE not in st.session_state:
        st.session_state[SK_SEARCH_MOVIE] = ""
    if SK_SEARCH_INPUT not in st.session_state:
        st.session_state[SK_SEARCH_INPUT] = ""


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def _short_username(name: str | None, max_len: int = 8) -> str:
    if not name:
        return "Guest"
    name = str(name).strip()
    if len(name) <= max_len:
        return name
    return name[: max_len - 1] + "…"


def _run_search(query: str):
    q = (query or "").strip()
    if not q:
        return False

    st.session_state[SK_SEARCH_MOVIE] = q
    st.session_state[SK_SEARCH_INPUT] = q

    u2 = st.session_state.get("user")
    if u2 and u2.get("user_id"):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO search_history (user_id, query)
                        VALUES (:uid, :q)
                        """
                    ),
                    {"uid": int(u2["user_id"]), "q": q[:255]},
                )
        except Exception:
            pass

    st.switch_page("pages/search.py")
    return True


def _queue_search(query: str):
    q = (query or "").strip()
    if q:
        st.session_state[SK_SEARCH_PENDING] = q
        st.rerun()


def _fetch_suggestions(q: str, limit: int = 4) -> list[str]:
    if len(q.strip()) < 2:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT DISTINCT title
                    FROM movies
                    WHERE title LIKE :pat
                      AND COALESCE(is_approved, 1) = 1
                    ORDER BY popularity DESC
                    LIMIT :lim
                    """
                ),
                {"pat": f"%{q.strip()}%", "lim": limit},
            ).fetchall()
        return [r[0] for r in rows if r and r[0]]
    except Exception:
        return []


def _header_styles():
    st.markdown(
        """
        <style>
        header {visibility:hidden;}
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        .block-container { padding-top: 0.4rem !important; max-width: 1380px; }

        /* MovieMind header shell (first bordered block on page) */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
            background: linear-gradient(
                135deg,
                var(--mm-card-bg) 0%,
                var(--mm-chat-wrap-bg) 55%,
                var(--mm-card-bg) 100%
            ) !important;
            border: 1px solid var(--mm-border) !important;
            border-radius: 16px !important;
            box-shadow:
                0 4px 20px rgba(0, 0, 0, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
            padding: 10px 14px !important;
            margin-bottom: 1.1rem !important;
            overflow: hidden !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
            overflow: hidden !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"] {
            flex: 0 1 auto !important;
            min-width: 0 !important;
            width: auto !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(2) {
            flex: 1 1 320px !important;
            min-width: 120px !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton > button {
            width: 100% !important;
            min-height: 38px !important;
            max-height: 38px !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 10px !important;
            border-radius: 10px !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            line-height: 1 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
            transition: transform 0.15s ease, filter 0.15s ease !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(1.06);
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] input {
            min-height: 38px !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 14px !important;
            border-radius: 10px !important;
            font-size: 0.88rem !important;
            border: 1px solid var(--mm-border) !important;
            background: var(--mm-input-bg, var(--mm-card-bg)) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.06) !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--mm-accent) !important;
            box-shadow: 0 0 0 2px color-mix(in srgb, var(--mm-accent) 35%, transparent) !important;
        }

        .mm-hdr-logo-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 38px;
            min-width: 44px;
        }
        .mm-hdr-logo-wrap a { line-height: 0; display: block; }
        .mm-hdr-logo-wrap img {
            height: 36px;
            width: auto;
            border-radius: 8px;
            display: block;
        }

        .mm-hdr-user {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            height: 38px;
            max-width: 100%;
            padding: 0 10px;
            border-radius: 10px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap !important;
            overflow: hidden;
            text-overflow: ellipsis;
            border: 1px solid var(--mm-border);
            background: color-mix(in srgb, var(--mm-accent) 12%, var(--mm-card-bg));
            color: var(--mm-text);
            box-sizing: border-box;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_header():
    restore_session()
    init_theme()
    track_site_time()
    apply_theme_css()
    _ensure_search_state()
    _header_styles()

    pending = st.session_state.pop(SK_SEARCH_PENDING, None)
    if pending:
        _run_search(pending)
        return

    logo = get_base64_image("assets/movieMind.png")
    u = st.session_state.get("user")
    is_admin = bool(u and u.get("role") == "admin")
    short_name = _short_username(u["username"] if u else None)
    full_name = html_lib.escape(u["username"] if u else "Guest")
    q_preview = st.session_state.get(SK_SEARCH_INPUT, "").strip()
    suggestions = _fetch_suggestions(q_preview)

    with st.container(border=True):
        # One row — integer ratios keep spacing stable; search column grows
        if u and is_admin:
            ratios = [1, 18, 2, 3, 3, 3, 1]
        elif u:
            ratios = [1, 20, 2, 3, 3, 1]
        else:
            ratios = [1, 20, 2, 3, 3, 1]

        cols = st.columns(ratios, gap="small")

        if u and is_admin:
            c_logo, c_search, c_go, c_user, c_prof, c_admin, c_hint = cols
        else:
            c_logo, c_search, c_go, c_user, c_prof, c_hint = cols
            c_admin = None

        with c_logo:
            st.markdown(
                f"""
                <div class="mm-hdr-logo-wrap">
                    <a href="/" target="_self" title="MovieMind Home">
                        <img src="data:image/png;base64,{logo}" alt="MovieMind"/>
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c_search:
            st.text_input(
                "Search",
                label_visibility="collapsed",
                placeholder="Search title, actor, genre…",
                key=SK_SEARCH_INPUT,
            )

        with c_go:
            if st.button("Go", key="hdr_search_btn", type="primary", use_container_width=True):
                q = st.session_state.get(SK_SEARCH_INPUT, "").strip()
                if q:
                    _queue_search(q)
                else:
                    st.toast("Type a search term first", icon="⚠️")

        with c_user:
            label = (
                f"👤 {html_lib.escape(short_name)}" if u else "👋 Guest"
            )
            st.markdown(
                f'<div class="mm-hdr-user" title="{full_name}">{label}</div>',
                unsafe_allow_html=True,
            )

        with c_prof:
            if u:
                if st.button("Profile", key="hdr_profile", use_container_width=True):
                    st.switch_page(
                        "pages/admin_profile.py"
                        if is_admin
                        else "pages/profile.py"
                    )
            else:
                if st.button("Login", key="hdr_login", use_container_width=True):
                    st.switch_page("pages/login.py")

        if c_admin is not None:
            with c_admin:
                if st.button("Admin", key="hdr_admin", use_container_width=True):
                    st.switch_page("pages/admin_auth.py")

        with c_hint:
            if suggestions:
                with st.popover("💡", use_container_width=True):
                    for i, title in enumerate(suggestions):
                        if st.button(
                            title[:36],
                            key=f"hdr_pop_{i}",
                            use_container_width=True,
                        ):
                            _queue_search(title)
