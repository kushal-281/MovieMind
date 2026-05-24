"""Theme-aware typography for About, FAQ, Privacy, Terms, Contact pages."""

import streamlit as st

from components.theme import _palette, init_theme


def apply_static_page_styles():
    """Use dark text on light themes and light text on dark themes via theme variables."""
    init_theme()
    p = _palette()

    st.markdown(
        f"""
        <style>
        .main-title, .title, .faq-title, .section-title, .heading {{
            color: {p["heading"]} !important;
        }}

        .sub-title, .subtitle, .faq-sub {{
            color: {p["muted_text"]} !important;
        }}

        .text, .mm-static-text, .team-box h3, .team-box p {{
            color: {p["text"]} !important;
        }}

        .team-box p {{
            color: {p["muted_text"]} !important;
        }}

        .heading {{
            border-left-color: {p["input_focus"]} !important;
        }}

        div[data-testid="stExpander"] details summary {{
            color: {p["heading"]} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stExpander"] details summary p,
        div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
            color: {p["heading"]} !important;
        }}

        div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {{
            color: {p["text"]} !important;
        }}

        .main .block-container hr {{
            border-top-color: {p["border"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
