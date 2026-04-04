import streamlit as st
import base64
import json
from cookies import cookies   # IMPORTANT

# ---------------- RESTORE SESSION FROM COOKIE ----------------
if "user" not in st.session_state:
    user_cookie = cookies.get("user")

    if user_cookie:
        try:
            st.session_state.user = json.loads(user_cookie)
        except:
            st.session_state.user = None
    else:
        st.session_state.user = None

# ---------------- DEFAULT SESSION ----------------
if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

if "search_input" not in st.session_state:
    st.session_state.search_input = ""

# ---------------- LOAD IMAGE ----------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# ---------------- HEADER ----------------
def show_header():

    logo = get_base64_image("assets/movieMind.png")

    st.markdown("""
    <style>
    header {visibility:hidden;}
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}

    .block-container {
        padding-top: 0rem !important;
        max-width:1350px;
    }

    .stButton > button {
        background-color: #808080;
        color: white;
        border-radius: 6px;
    }

    /* USERNAME LEFT MARGIN */
    .user-name {
        margin-left: 20px;
        margin-top: 5px;
    }

    /* PROFILE BUTTON LEFT MARGIN */
    div[data-testid="column"]:nth-child(3) .stButton > button {
        margin-left: 10px;
    }

    /* SEARCH BAR TOP MARGIN */
    div[data-testid="stTextInput"] > div > div > input {
        margin-top: -10px !important;
    }

    /* SEARCH BUTTON MARGIN */
    div[data-testid="column"]:nth-child(2) .stButton > button {
        margin-top: 50px;
        margin-left: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([6,1,1,1])

    # LOGO
    with col1:
        st.markdown(
            f"<img src='data:image/png;base64,{logo}' height='40'>",
            unsafe_allow_html=True
        )

    # ---------------- USER LOGGED IN ----------------
    if st.session_state.user:

        with col2:
            st.markdown(
                f"<div class='user-name'>👤 {st.session_state.user['username']}</div>",
                unsafe_allow_html=True
            )

        with col3:
            if st.button("Profile", key="profile_btn"):
                st.switch_page("pages/profile.py")

    # ---------------- USER NOT LOGGED IN ----------------
    else:
        with col4:
            if st.button("Login", key="login_btn"):
                st.switch_page("pages/login.py")

    st.divider()

    # ---------------- SEARCH ----------------
    col5, col6 = st.columns([6,1])

    with col5:
        st.text_input("", placeholder="Search movies...", key="search_input")

    with col6:
        if st.button("Search", key="search_btn"):
            if st.session_state.search_input.strip():
                st.session_state.search_movie = st.session_state.search_input
                st.switch_page("pages/search.py")