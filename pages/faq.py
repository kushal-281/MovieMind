import streamlit as st
import pandas as pd
from sqlalchemy import text

from components.footer import show_footer
from components.header_without_search import header_without_search
from config.database import engine, ensure_schema

st.set_page_config(page_title="FAQ - MovieMind", layout="wide")
ensure_schema()
header_without_search()

st.markdown(
    """
    <style>
    .faq-title {
        font-size: 2rem;
        font-weight: 700;
        color: #dbe4ff;
        margin-bottom: 0.3rem;
    }
    .faq-sub {
        color: #b5bfd6;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="faq-title">Frequently Asked Questions</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="faq-sub">Click on any question to view the answer.</div>',
    unsafe_allow_html=True,
)

default_faqs = [
    {
        "question": "How do I create an account on MovieMind?",
        "answer": "Go to the Signup page, fill in your details, and submit the form.",
    },
    {
        "question": "Why am I not seeing recommendations?",
        "answer": "Watch or search a few movies first. Recommendations improve with your activity.",
    },
    {
        "question": "Can I save movies for later?",
        "answer": "Yes. Use the Favorites feature to save movies and view them anytime.",
    },
    {
        "question": "How can I contact support?",
        "answer": "Use the Contact Us page to submit your issue or question.",
    },
    {
        "question": "How do I reset my login session?",
        "answer": "Logout from your profile and login again to refresh your session.",
    },
]

faqs = []
try:
    with engine.connect() as conn:
        db_faqs = pd.read_sql(
            text(
                """
                SELECT faq_id, question, answer
                FROM faqs
                WHERE is_active = 1
                ORDER BY updated_at DESC, faq_id DESC
                """
            ),
            conn,
        )
    if not db_faqs.empty:
        faqs = db_faqs.to_dict("records")
except Exception:
    faqs = []

if not faqs:
    faqs = default_faqs

for idx, item in enumerate(faqs):
    question = str(item.get("question", "")).strip()
    answer = str(item.get("answer", "")).strip()
    if not question or not answer:
        continue
    with st.expander(f"❯ {question}"):
        st.markdown(answer)

show_footer()