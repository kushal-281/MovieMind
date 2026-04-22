"""Movie / recommendation chat UI + persistence to chat_logs."""

import pandas as pd
import streamlit as st
from sqlalchemy import text
import html

from config.database import engine
from ml.recommendation_engine import recommend


def _format_recommendation_answer(prompt: str, picks: list[dict]) -> str:
    lines = [f"### Recommendations for: _{prompt}_", ""]
    for idx, m in enumerate(picks, start=1):
        title = m.get("title") or "Unknown"
        rating = m.get("rating")
        rating_txt = f"{float(rating):.1f}" if rating is not None else "N/A"
        lines.append(f"{idx}. **{title}**  \n   - Rating: `{rating_txt}`")
    lines.append("")
    lines.append("You can ask by mood, genre, actor, year, or similar story type.")
    return "\n".join(lines)


def _answer_catalog_questions(prompt: str) -> str | None:
    q = prompt.lower()
    try:
        with engine.connect() as conn:
            if any(k in q for k in ["top rated", "best movie", "highest rated"]):
                df = pd.read_sql(
                    text(
                        """
                        SELECT title, vote_average
                        FROM movies
                        WHERE vote_count > 100
                        ORDER BY vote_average DESC, vote_count DESC
                        LIMIT 5
                        """
                    ),
                    conn,
                )
                if not df.empty:
                    body = "\n".join(
                        [
                            f"- **{r['title']}** (Rating: {float(r['vote_average']):.1f})"
                            for _, r in df.iterrows()
                        ]
                    )
                    return f"### Top Rated Movies\n{body}"

            if any(k in q for k in ["latest", "new movie", "recent movie"]):
                df = pd.read_sql(
                    text(
                        """
                        SELECT title, release_date
                        FROM movies
                        WHERE release_date IS NOT NULL
                        ORDER BY release_date DESC
                        LIMIT 5
                        """
                    ),
                    conn,
                )
                if not df.empty:
                    body = "\n".join(
                        [f"- **{r['title']}** ({r['release_date']})" for _, r in df.iterrows()]
                    )
                    return f"### Latest Movies\n{body}"
    except Exception:
        return None
    return None


def _answer_website_questions(prompt: str) -> str | None:
    q = prompt.lower()

    if any(k in q for k in ["hello", "hi", "hey", "good morning", "good evening"]):
        return (
            "Hi! I can help with:\n"
            "- Movie recommendations\n"
            "- Top/latest movies in catalog\n"
            "- How to use MovieMind pages (search, profile, favorites, contact)\n"
            "- FAQ/help questions"
        )
    if any(k in q for k in ["profile", "account", "analytics"]):
        return (
            "Open your **Profile** page to use chatbot, view search/chat history, "
            "and check your personal analytics."
        )
    if any(k in q for k in ["admin", "dashboard", "manage faq", "contact reply"]):
        return (
            "Admins can open **Admin Profile** to access the dashboard, user activity, "
            "chat logs, contact reply panel, and FAQ manager."
        )
    if any(k in q for k in ["forgot password", "reset password", "otp"]):
        return (
            "Use the **Forgot Password** button on the login page. "
            "MovieMind will email an OTP. Verify OTP and set your new password."
        )
    if any(k in q for k in ["contact", "support", "help email"]):
        return "You can use the **Contact** page or email support at `support@moviemind.com`."
    return None


def _answer_faq(prompt: str) -> str | None:
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT question, answer
                    FROM faqs
                    WHERE is_active = 1
                      AND (
                        LOWER(question) LIKE CONCAT('%', LOWER(:q), '%')
                        OR LOWER(:q) LIKE CONCAT('%', LOWER(question), '%')
                      )
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """
                ),
                {"q": prompt.strip()},
            ).fetchone()
            if row:
                return f"### FAQ match\n**Q:** {row[0]}\n\n**A:** {row[1]}"
    except Exception:
        return None
    return None


def render_movie_chatbot(user_id: int):
    st.subheader("💬 MovieMind Assistant")
    st.caption("Ask about movies, get recommendations, or describe what you feel like watching.")
    st.markdown(
        """
        <style>
        .mm-chat-wrap {
            max-height: 460px;
            overflow-y: auto;
            border: 1px solid rgba(140, 162, 255, 0.22);
            border-radius: 14px;
            padding: 10px;
            background: linear-gradient(180deg, #111626 0%, #0f1422 100%);
        }
        .mm-chat-msg {
            padding: 10px 12px;
            border-radius: 12px;
            margin: 8px 0;
            line-height: 1.4;
            white-space: pre-wrap;
        }
        .mm-user {
            background: #3a2c58;
            border: 1px solid rgba(207, 164, 255, 0.35);
            margin-left: 18%;
            color: #efe9ff;
        }
        .mm-bot {
            background: #1f3b35;
            border: 1px solid rgba(114, 210, 180, 0.35);
            margin-right: 18%;
            color: #e6fff7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
        bubble_html = ['<div class="mm-chat-wrap">']
        for _, c in chats.iloc[::-1].iterrows():
            q = html.escape(str(c["query"]))
            r = html.escape(str(c["response"]))
            ts = html.escape(str(c["timestamp"]))
            bubble_html.append(f'<div class="mm-chat-msg mm-user">{q}</div>')
            bubble_html.append(f'<div class="mm-chat-msg mm-bot">{r}\n\n{ts}</div>')
        bubble_html.append("</div>")
        st.markdown("".join(bubble_html), unsafe_allow_html=True)
    else:
        st.info("No chat history yet. Ask your first question.")

    with st.form("chat_prompt_form", clear_on_submit=True):
        prompt = st.text_input("Message the bot...", key="chat_prompt_input")
        submitted = st.form_submit_button("Send", use_container_width=True)
    if not submitted or not prompt or not str(prompt).strip():
        return

    q = str(prompt).strip()
    try:
        website_answer = _answer_website_questions(q)
        faq_answer = _answer_faq(q)
        catalog_answer = _answer_catalog_questions(q)
        if website_answer:
            answer = website_answer
        elif faq_answer:
            answer = faq_answer
        elif catalog_answer:
            answer = catalog_answer
        else:
            recs = recommend(q) or []
            top = recs[:6]
            if top:
                answer = _format_recommendation_answer(q, top)
            else:
                answer = (
                    "### I could not find a strong match\n"
                    "- Try full movie names, actors, genres, moods, or years.\n"
                    "- Example: `thriller movies like Inception` or `feel-good comedy`."
                )
    except Exception as e:
        answer = f"### Sorry, I hit an error\n`{e}`"

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
