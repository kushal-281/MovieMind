import streamlit as st

from cookies import cookies

THEMES = {
    "dark": {
        "text": "#FFFFFF",
        "muted_text": "#B0B0B0",
        "input_focus": "#4F8BF9",
        "app_bg": "#0E1117",
        "sidebar_bg": "#161B22",
        "heading": "#FFFFFF",
        "card_bg": "#1E2633",
        "button_bg": "#4F8BF9",
        "button_text": "#FFFFFF",
        "button_border": "#4F8BF9",
        "button_hover_bg": "#2563EB",
        "chat_wrap_bg": "#161B22",
        "chat_user_bg": "#2563EB",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#1E2633",
        "chat_bot_text": "#FFFFFF",
        "chat_border": "#2D3748",
        "pill_bg": "#1E2633",
        "pill_text": "#E2E8F0",
        "input_bg": "#161B22",
        "border": "#2D3748",
    },
    "light": {
        "text": "#1a1a2e",
        "muted_text": "#4a5568",
        "input_focus": "#2563EB",
        "app_bg": "#f8fafc",
        "sidebar_bg": "#ffffff",
        "heading": "#0f172a",
        "card_bg": "#ffffff",
        "button_bg": "#2563EB",
        "button_text": "#FFFFFF",
        "button_border": "#2563EB",
        "button_hover_bg": "#1d4ed8",
        "chat_wrap_bg": "#eef2ff",
        "chat_user_bg": "#2563EB",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#ffffff",
        "chat_bot_text": "#1e293b",
        "chat_border": "#cbd5e1",
        "pill_bg": "#e2e8f0",
        "pill_text": "#0f172a",
        "input_bg": "#ffffff",
        "border": "#cbd5e1",
    },
    "light_cream": {
        "text": "#3d3429",
        "muted_text": "#6b5d4f",
        "input_focus": "#c2410c",
        "app_bg": "#faf6f0",
        "sidebar_bg": "#fffdf8",
        "heading": "#292018",
        "card_bg": "#fffefb",
        "button_bg": "#ea580c",
        "button_text": "#FFFFFF",
        "button_border": "#ea580c",
        "button_hover_bg": "#c2410c",
        "chat_wrap_bg": "#f5ebe0",
        "chat_user_bg": "#ea580c",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#fffefb",
        "chat_bot_text": "#3d3429",
        "chat_border": "#e7d5c4",
        "pill_bg": "#f5ebe0",
        "pill_text": "#292018",
        "input_bg": "#fffefb",
        "border": "#e7d5c4",
    },
    "light_sky": {
        "text": "#0c4a6e",
        "muted_text": "#0369a1",
        "input_focus": "#0284c7",
        "app_bg": "#f0f9ff",
        "sidebar_bg": "#ffffff",
        "heading": "#082f49",
        "card_bg": "#ffffff",
        "button_bg": "#0284c7",
        "button_text": "#FFFFFF",
        "button_border": "#0284c7",
        "button_hover_bg": "#0369a1",
        "chat_wrap_bg": "#e0f2fe",
        "chat_user_bg": "#0284c7",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#ffffff",
        "chat_bot_text": "#0c4a6e",
        "chat_border": "#bae6fd",
        "pill_bg": "#e0f2fe",
        "pill_text": "#082f49",
        "input_bg": "#ffffff",
        "border": "#bae6fd",
    },
    "midnight": {
        "text": "#e8e6ff",
        "muted_text": "#a89fd4",
        "input_focus": "#a855f7",
        "app_bg": "#0a0612",
        "sidebar_bg": "#120a1f",
        "heading": "#f5f3ff",
        "card_bg": "#1a1030",
        "button_bg": "#7c3aed",
        "button_text": "#FFFFFF",
        "button_border": "#7c3aed",
        "button_hover_bg": "#6d28d9",
        "chat_wrap_bg": "#120a1f",
        "chat_user_bg": "#7c3aed",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#1a1030",
        "chat_bot_text": "#ede9fe",
        "chat_border": "#3b2667",
        "pill_bg": "#2d1b4e",
        "pill_text": "#ede9fe",
        "input_bg": "#120a1f",
        "border": "#3b2667",
    },
    "ocean": {
        "text": "#e0f7fa",
        "muted_text": "#80cbc4",
        "input_focus": "#00bcd4",
        "app_bg": "#051419",
        "sidebar_bg": "#0a232e",
        "heading": "#e0f7fa",
        "card_bg": "#0d2d3a",
        "button_bg": "#00838f",
        "button_text": "#FFFFFF",
        "button_border": "#00838f",
        "button_hover_bg": "#006064",
        "chat_wrap_bg": "#0a232e",
        "chat_user_bg": "#00838f",
        "chat_user_text": "#FFFFFF",
        "chat_bot_bg": "#0d2d3a",
        "chat_bot_text": "#e0f7fa",
        "chat_border": "#1a4a5c",
        "pill_bg": "#0d2d3a",
        "pill_text": "#e0f7fa",
        "input_bg": "#0a232e",
        "border": "#1a4a5c",
    },
}


def init_theme():
    if "theme_mode" in st.session_state:
        return
    saved = None
    try:
        if cookies.ready():
            saved = cookies.get("theme_mode")
    except Exception:
        pass
    mode = saved if saved in THEMES else "dark"
    st.session_state["theme_mode"] = mode


def save_theme(mode: str):
    if mode not in THEMES:
        mode = "dark"
    st.session_state["theme_mode"] = mode
    try:
        if cookies.ready():
            cookies["theme_mode"] = mode
            cookies.save()
    except Exception:
        pass


def _palette():
    init_theme()
    mode = st.session_state.get("theme_mode", "dark")
    if mode not in THEMES:
        mode = "dark"
    return THEMES[mode]


def apply_theme_css():
    p = _palette()

    st.markdown(
        f"""
        <style>
        :root {{
            --mm-text: {p["text"]};
            --mm-muted: {p["muted_text"]};
            --mm-accent: {p["input_focus"]};
            --mm-card-bg: {p["card_bg"]};
            --mm-border: {p["border"]};
            --mm-chat-wrap-bg: {p["chat_wrap_bg"]};
            --mm-chat-user-bg: {p["chat_user_bg"]};
            --mm-chat-user-text: {p["chat_user_text"]};
            --mm-chat-bot-bg: {p["chat_bot_bg"]};
            --mm-chat-bot-text: {p["chat_bot_text"]};
            --mm-chat-border: {p["chat_border"]};
        }}

        .stApp {{
            background: {p["app_bg"]} !important;
            color: {p["text"]} !important;
        }}

        [data-testid="stSidebar"] {{
            background: {p["sidebar_bg"]} !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {p["heading"]} !important;
            font-weight: 700 !important;
        }}

        p, label, li, small, span {{
            color: {p["text"]};
        }}

        [data-testid="stMarkdownContainer"] p {{
            color: {p["text"]};
        }}

        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {p["muted_text"]} !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: {p["card_bg"]} !important;
            border-color: {p["border"]} !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background: {p["input_bg"]} !important;
            color: {p["text"]} !important;
            border-color: {p["border"]} !important;
        }}

        div.stButton > button {{
            background: {p["button_bg"]} !important;
            color: {p["button_text"]} !important;
            border-radius: 10px !important;
            border: 1px solid {p["button_border"]} !important;
            font-weight: 600 !important;
        }}

        div.stButton > button:hover {{
            background: {p["button_hover_bg"]} !important;
            border-color: {p["button_hover_bg"]} !important;
        }}

        div[data-testid="stFormSubmitButton"] > button {{
            background: {p["button_bg"]} !important;
            color: {p["button_text"]} !important;
        }}

        .mm-user-pill {{
            background: {p["pill_bg"]} !important;
            color: {p["pill_text"]} !important;
        }}

        hr {{
            border-color: {p["border"]} !important;
        }}

        div[data-testid="stTabs"] button {{
            color: {p["muted_text"]} !important;
        }}

        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {p["input_focus"]} !important;
            border-color: {p["input_focus"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def auth_page_styles():
    """Shared layout for login / signup / forgot password."""
    p = _palette()
    st.markdown(
        f"""
        <style>
        header {{visibility:hidden;}}
        #MainMenu {{visibility:hidden;}}
        footer {{visibility:hidden;}}

        .block-container {{
            max-width: 1250px;
            margin-left: auto;
            margin-right: auto;
            padding-top: 0.5rem !important;
        }}

        .mm-auth-card {{
            background: {p["card_bg"]};
            border: 1px solid {p["border"]};
            border-radius: 16px;
            padding: 8px 4px;
        }}

        div.stButton > button {{
            width: 100% !important;
            min-height: 44px !important;
        }}

        div[data-testid="column"] div.stButton > button {{
            width: 100% !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
