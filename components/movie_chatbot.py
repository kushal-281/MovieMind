"""Movie / recommendation chat UI + persistence to chat_logs."""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from config.database import engine
from ml.recommendation_engine import recommend


def render_movie_chatbot(user_id: int):
    st.subheader("💬 MovieMind Assistant")
    st.caption("Ask about movies, get recommendations, or describe what you feel like watching.")

    try:
        q_hist = text(
            """
            SELECT query, response, timestamp
            FROM chat_logs
            WHERE user_id = :uid
            ORDER BY timestamp DESC
            LIMIT 30
            """
        )
        with engine.connect() as conn:
            chats = pd.read_sql(q_hist, conn, params={"uid": user_id})
    except Exception:
        chats = pd.DataFrame()

    if not chats.empty:
        for _, c in chats.iloc[::-1].iterrows():
            with st.chat_message("user"):
                st.write(c["query"])
            with st.chat_message("assistant"):
                st.write(c["response"])
                st.caption(str(c["timestamp"]))

    prompt = st.chat_input("Message the bot…")
    if not prompt or not str(prompt).strip():
        return

    q = str(prompt).strip()
    try:
        recs = recommend(q) or []
        top = recs[:6]
        if top:
            lines = []
            for m in top:
                t = m.get("title")
                r = m.get("rating")
                if t:
                    lines.append(f"• {t}" + (f" (rating {r})" if r is not None else ""))
            answer = "Here are some picks that match your message:\n" + "\n".join(lines)
        else:
            answer = (
                "I couldn’t find strong matches in the catalog. "
                "Try a movie title, actor name, genre, or mood (e.g. “feel-good comedy”)."
            )
    except Exception as e:
        answer = f"Sorry, something went wrong while searching: {e}"

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO chat_logs (user_id, query, response) VALUES (:uid, :q, :r)"
                ),
                {"uid": user_id, "q": q, "r": answer},
            )
    except Exception:
        pass

    st.rerun()
