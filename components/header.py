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

        /* Image-1 style header shell */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
            background: linear-gradient(145deg, #050a18 0%, #0a1228 50%, #050a18 100%) !important;
            border: 1px solid rgba(79, 139, 249, 0.45) !important;
            border-radius: 22px !important;
            box-shadow:
                0 0 0 1px rgba(106, 13, 173, 0.25),
                0 0 28px rgba(37, 99, 235, 0.18),
                0 8px 32px rgba(0, 0, 0, 0.45),
                inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
            padding: 12px 18px !important;
            margin-bottom: 1.15rem !important;
            overflow: hidden !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 12px !important;
            width: 100% !important;
            overflow: hidden !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"] {
            flex: 0 1 auto !important;
            min-width: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(2) {
            flex: 0 1 240px !important;
            max-width: 260px !important;
            min-width: 160px !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(2) div[data-testid="stTextInput"] {
            max-width: 260px !important;
        }

        /* Push user / profile / admin to the right after narrower search */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(4) {
            margin-left: auto !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }

        /* Default header buttons */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton > button {
            width: 100% !important;
            min-height: 42px !important;
            max-height: 42px !important;
            height: 42px !important;
            margin: 0 !important;
            padding: 0 14px !important;
            border-radius: 12px !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            line-height: 1 !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }

        /* Go button — blue/purple gradient */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(3) div.stButton > button {
            background: linear-gradient(180deg, #3b82f6 0%, #6366f1 55%, #7c3aed 100%) !important;
            border: 1px solid rgba(129, 140, 248, 0.65) !important;
            color: #fff !important;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.45) !important;
        }

        /* Profile / Login — dark pill + bottom glow */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(5) div.stButton > button {
            background: linear-gradient(180deg, #0c1428 0%, #0a1020 100%) !important;
            border: 1px solid rgba(79, 139, 249, 0.4) !important;
            color: #e8eeff !important;
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35), inset 0 -2px 0 rgba(59, 130, 246, 0.5) !important;
        }

        /* Admin button */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:nth-child(6) div.stButton > button {
            background: linear-gradient(180deg, #1a1030 0%, #120820 100%) !important;
            border: 1px solid rgba(124, 58, 237, 0.45) !important;
            color: #ede9fe !important;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
        }

        /* Suggestions popover trigger */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        [data-testid="column"]:last-child div.stButton > button {
            background: rgba(10, 20, 40, 0.9) !important;
            border: 1px solid rgba(79, 139, 249, 0.35) !important;
            color: #fbbf24 !important;
            min-width: 42px !important;
            padding: 0 8px !important;
            box-shadow: 0 0 12px rgba(251, 191, 36, 0.2) !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div.stButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(1.08);
        }

        /* Search bar — glowing border + search icon padding */
        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] input {
            min-height: 42px !important;
            height: 42px !important;
            margin: 0 !important;
            padding: 0 40px 0 38px !important;
            border-radius: 12px !important;
            font-size: 0.86rem !important;
            color: #c8d4f0 !important;
            background: rgba(6, 12, 28, 0.95) !important;
            border: 1px solid rgba(59, 130, 246, 0.55) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow:
                0 0 14px rgba(37, 99, 235, 0.22),
                inset 0 1px 4px rgba(0, 0, 0, 0.35) !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] input::placeholder {
            color: #6b7a99 !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] input:focus {
            border-color: rgba(96, 165, 250, 0.9) !important;
            box-shadow:
                0 0 0 2px rgba(59, 130, 246, 0.35),
                0 0 20px rgba(59, 130, 246, 0.25) !important;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] > div {
            position: relative;
        }

        .main .block-container > div > div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type
        div[data-testid="stTextInput"] > div::before {
            content: "🔍";
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.95rem;
            z-index: 2;
            pointer-events: none;
            opacity: 0.85;
        }

        /* Brand block (logo + MovieMind + tagline) */
        .mm-brand-block {
            display: flex;
            align-items: center;
            gap: 10px;
            height: 42px;
            min-width: 0;
            white-space: nowrap;
        }
        .mm-brand-block a {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none !important;
            color: inherit;
        }
        .mm-brand-block img {
            height: 38px;
            width: auto;
            border-radius: 8px;
            flex-shrink: 0;
        }
        .mm-brand-titles {
            display: flex;
            flex-direction: column;
            justify-content: center;
            line-height: 1.15;
            min-width: 0;
        }
        .mm-brand-title {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            white-space: nowrap;
            background: linear-gradient(
                135deg,
                var(--mm-accent) 0%,
                color-mix(in srgb, var(--mm-accent) 55%, #c4b5fd) 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .mm-brand-tag {
            font-size: 0.62rem;
            font-weight: 500;
            color: #7a8ba8;
            letter-spacing: 0.04em;
            white-space: nowrap;
        }

        /* User pill */
        .mm-hdr-user {
            display: inline-flex;
            align-items: center;
            justify-content: flex-start;
            gap: 8px;
            height: 42px;
            width: 100%;
            max-width: 100%;
            padding: 0 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 700;
            white-space: nowrap !important;
            overflow: hidden;
            text-overflow: ellipsis;
            border: 1px solid rgba(79, 139, 249, 0.35);
            background: linear-gradient(180deg, rgba(12, 20, 40, 0.95), rgba(8, 14, 30, 0.98));
            color: #ffffff !important;
            box-sizing: border-box;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }
        .mm-hdr-user .mm-user-ico {
            font-size: 1rem;
            opacity: 0.95;
            flex-shrink: 0;
            color: #ffffff !important;
        }
        .mm-hdr-user .mm-user-name {
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
            color: #ffffff !important;
        }
        .mm-hdr-user .mm-online-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.75);
            flex-shrink: 0;
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
            ratios = [2.6, 7, 1.3, 2.6, 2.4, 2.2, 0.7]
        elif u:
            ratios = [2.6, 7.5, 1.3, 2.6, 2.6, 0.7]
        else:
            ratios = [2.6, 7.5, 1.3, 2.4, 2.6, 0.7]

        cols = st.columns(ratios, gap="small")

        if u and is_admin:
            c_logo, c_search, c_go, c_user, c_prof, c_admin, c_hint = cols
        else:
            c_logo, c_search, c_go, c_user, c_prof, c_hint = cols
            c_admin = None

        with c_logo:
            st.markdown(
                f"""
                <div class="mm-brand-block">
                    <a href="/" target="_self" title="MovieMind Home">
                        <img src="data:image/png;base64,{logo}" alt="MovieMind"/>
                        <span class="mm-brand-titles">
                            <span class="mm-brand-title">MovieMind</span>
                            <span class="mm-brand-tag">Find. Watch. Enjoy.</span>
                        </span>
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
            if u:
                st.markdown(
                    f"""
                    <div class="mm-hdr-user" title="{full_name}">
                        <span class="mm-user-ico">👤</span>
                        <span class="mm-user-name">{html_lib.escape(short_name)}</span>
                        <span class="mm-online-dot"></span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="mm-hdr-user">
                        <span class="mm-user-ico">👋</span>
                        <span class="mm-user-name">Guest</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with c_prof:
            if u:
                if st.button("👤 Profile", key="hdr_profile", use_container_width=True):
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
                with st.popover("✨", use_container_width=True):
                    for i, title in enumerate(suggestions):
                        if st.button(
                            title[:36],
                            key=f"hdr_pop_{i}",
                            use_container_width=True,
                        ):
                            _queue_search(title)
