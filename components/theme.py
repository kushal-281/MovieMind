import streamlit as st

from cookies import cookies

THEMES = {
    "light": {
        "app_bg": "linear-gradient(180deg, #f7fbff 0%, #eef4ff 100%)",
        "sidebar_bg": "#f4f8ff",
        "text": "#1c2540",
        "button_bg": "linear-gradient(180deg, #c7dcff 0%, #a8c9ff 100%)",
        "button_hover_bg": "linear-gradient(180deg, #b9d3ff 0%, #98beff 100%)",
        "button_text": "#000000",
        "button_border": "#7ea9e8",
        "input_bg": "#ffffff",
        "input_text": "#10151f",
        "input_border": "#8db6f0",
        "input_focus": "#4e89df",
    },
    "dark": {
        "app_bg": "linear-gradient(180deg, #0f1422 0%, #101827 100%)",
        "sidebar_bg": "#111a2c",
        "text": "#e8ecff",
        "button_bg": "linear-gradient(180deg, #374a79 0%, #2f3f65 100%)",
        "button_hover_bg": "linear-gradient(180deg, #42588f 0%, #36507f 100%)",
        "button_text": "#f5f7ff",
        "button_border": "#5870ac",
        "input_bg": "#1a2640",
        "input_text": "#f2f6ff",
        "input_border": "#5d73ac",
        "input_focus": "#80a0ef",
    },
    "sunset": {
        "app_bg": "linear-gradient(180deg, #fff4e8 0%, #ffe7d7 100%)",
        "sidebar_bg": "#ffeede",
        "text": "#3b1f1f",
        "button_bg": "linear-gradient(180deg, #ffbd8b 0%, #ff9f66 100%)",
        "button_hover_bg": "linear-gradient(180deg, #ffb079 0%, #ff9159 100%)",
        "button_text": "#1e0e00",
        "button_border": "#da7f4a",
        "input_bg": "#fff8f1",
        "input_text": "#442014",
        "input_border": "#e49b6a",
        "input_focus": "#d0703f",
    },
    "forest": {
        "app_bg": "linear-gradient(180deg, #e9f6ef 0%, #dff1e7 100%)",
        "sidebar_bg": "#e6f3eb",
        "text": "#1e3a2f",
        "button_bg": "linear-gradient(180deg, #79c29a 0%, #5cad83 100%)",
        "button_hover_bg": "linear-gradient(180deg, #6db88f 0%, #4fa277 100%)",
        "button_text": "#0d241b",
        "button_border": "#3f8f68",
        "input_bg": "#f4fff8",
        "input_text": "#163428",
        "input_border": "#69b28a",
        "input_focus": "#2f8f66",
    },
    "ocean": {
        "app_bg": "linear-gradient(180deg, #e9f8ff 0%, #d9efff 100%)",
        "sidebar_bg": "#e0f3ff",
        "text": "#12324a",
        "button_bg": "linear-gradient(180deg, #77b8e8 0%, #5f9fd1 100%)",
        "button_hover_bg": "linear-gradient(180deg, #69acd9 0%, #4f90c4 100%)",
        "button_text": "#071d2c",
        "button_border": "#3f82b8",
        "input_bg": "#f3fbff",
        "input_text": "#12324a",
        "input_border": "#69aeda",
        "input_focus": "#2f7eb6",
    },
    "lavender": {
        "app_bg": "linear-gradient(180deg, #f6f0ff 0%, #ece1ff 100%)",
        "sidebar_bg": "#f0e8ff",
        "text": "#2f2148",
        "button_bg": "linear-gradient(180deg, #bea6f8 0%, #a48aec 100%)",
        "button_hover_bg": "linear-gradient(180deg, #b094f5 0%, #967be7 100%)",
        "button_text": "#1e1238",
        "button_border": "#8565d1",
        "input_bg": "#fcf9ff",
        "input_text": "#2f2148",
        "input_border": "#b29de9",
        "input_focus": "#7a5bc8",
    },
}


def init_theme():
    # Default website theme is light unless user already selected one.
    if "theme_mode" not in st.session_state:
        saved = cookies.get("theme_mode")
        st.session_state.theme_mode = saved if saved in THEMES else "light"


def save_theme(mode: str):
    if mode not in THEMES:
        mode = "light"
    st.session_state.theme_mode = mode
    cookies["theme_mode"] = mode
    cookies.save()


def apply_theme_css():
    init_theme()
    mode = st.session_state.get("theme_mode", "light")
    palette = THEMES.get(mode, THEMES["light"])
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {palette["app_bg"]};
            color: {palette["text"]};
        }}
        [data-testid="stSidebar"] {{
            background: {palette["sidebar_bg"]};
        }}
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        label, .stCaption {{
            color: {palette["text"]} !important;
        }}

        /* Unified button styles for all themes */
        div.stButton > button,
        div.stFormSubmitButton > button {{
            background: {palette["button_bg"]} !important;
            color: {palette["button_text"]} !important;
            border: 1px solid {palette["button_border"]} !important;
            border-radius: 9px !important;
            font-weight: 600 !important;
        }}
        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {{
            background: {palette["button_hover_bg"]} !important;
            color: {palette["button_text"]} !important;
            border: 1px solid {palette["button_border"]} !important;
        }}

        /* Theme-aware input fields */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTimeInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background: {palette["input_bg"]} !important;
            color: {palette["input_text"]} !important;
            border: 1px solid {palette["input_border"]} !important;
            border-radius: 8px !important;
        }}
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stNumberInput"] input::placeholder {{
            color: {palette["input_text"]} !important;
            opacity: 0.65;
        }}
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stDateInput"] input:focus,
        div[data-testid="stTimeInput"] input:focus {{
            border: 1px solid {palette["input_focus"]} !important;
            box-shadow: 0 0 0 1px {palette["input_focus"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
