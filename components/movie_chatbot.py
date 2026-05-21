"""Interactive MovieMind chat assistant with human-style replies."""

import os
import html
import random

import pandas as pd
import streamlit as st
from sqlalchemy import text

from config.database import engine, ensure_schema
from ml.recommendation_engine import recommend

QUICK_PROMPTS = [
    "Hello",
    "Top rated movies",
    "Latest releases",
    "Suggest action movies",
    "Bollywood romance",
    "I'm bored, surprise me",
]

SYSTEM_PROMPT = """You are MovieMind — a warm, enthusiastic movie buddy.
Reply in 2-4 short paragraphs like a friend. Use the user's name if given.
Use numbered lists for recommendations. No markdown headers (no ###).
"""


def _esc(text: str) -> str:
    return html.escape(str(text or "")).replace("\n", "<br>")


def _human_greeting(username: str | None) -> str:
    name = username or "there"
    return (
        f"Hey {name}! I'm your MovieMind buddy.\n\n"
        "Tell me a mood, genre, actor, or a movie you loved — I'll find picks for you.\n\n"
        "Tap a quick prompt below or type your question and hit Send."
    )


def _human_recommendations(prompt: str, picks: list[dict]) -> str:
    intro = random.choice(
        [
            "Here's what I'd put on your watchlist:",
            "I found some great matches for you:",
            "Based on that, I'd queue these:",
        ]
    )
    lines = [intro, ""]
    for idx, m in enumerate(picks[:6], start=1):
        title = m.get("title") or "Unknown"
        rating = m.get("rating")
        rtxt = f"{float(rating):.1f}/10" if rating is not None else "unrated"
        lines.append(f"{idx}. {title} — {rtxt}")
    lines.append("")
    lines.append("Want Hollywood, Bollywood, or a specific year? Just say the word.")
    return "\n".join(lines)


def _human_catalog_top(df: pd.DataFrame) -> str:
    if df.empty:
        return "I couldn't load top picks right now — try 'action' or a movie title."
    lines = ["These are fan favourites on MovieMind right now:", ""]
    for _, r in df.iterrows():
        lines.append(f"• {r['title']} — {float(r['vote_average']):.1f} stars")
    lines.append("")
    lines.append("Pick one and I can suggest similar titles!")
    return "\n".join(lines)


def _human_catalog_latest(df: pd.DataFrame) -> str:
    if df.empty:
        return "No recent releases in the catalog yet — check back soon!"
    lines = ["Fresh on MovieMind:", ""]
    for _, r in df.iterrows():
        lines.append(f"• {r['title']} ({r['release_date']})")
    lines.append("")
    lines.append("Want something in the same genre?")
    return "\n".join(lines)


def _db_search_movies(query: str, limit: int = 6) -> list[dict]:
    """Direct DB search when ML recommend() returns nothing."""
    ensure_schema()
    q = query.strip()
    if not q:
        return []
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text(
                    """
                    SELECT movie_id, title, vote_average, poster_path
                    FROM movies
                    WHERE COALESCE(is_approved, 1) = 1
                      AND (
                        title LIKE :q
                        OR overview LIKE :q
                        OR industry LIKE :q
                      )
                    ORDER BY popularity DESC
                    LIMIT :lim
                    """
                ),
                conn,
                params={"q": f"%{q}%", "lim": limit},
            )
        if df.empty:
            return []
        return [
            {
                "id": int(r["movie_id"]),
                "title": r["title"],
                "rating": float(r["vote_average"] or 0),
                "poster": r.get("poster_path"),
            }
            for _, r in df.iterrows()
        ]
    except Exception:
        return []


def _answer_website_questions(prompt: str, username: str | None) -> str | None:
    q = prompt.lower()
    name = username or "friend"

    if any(k in q for k in ["hello", "hi", "hey", "howdy"]):
        return _human_greeting(username)

    if "thank" in q:
        return f"You're welcome, {name}! Ask me anytime for more picks."

    if "who are you" in q or "what are you" in q:
        return (
            "I'm MovieMind's movie buddy — I help you discover films, "
            "top lists, and what's trending in our catalog."
        )

    if "profile" in q:
        return (
            f"{name}, open Profile for chat history, Add Movie, analytics, and themes."
        )

    if "add movie" in q:
        return "Go to Profile → Add Movie to submit a missing title for admin review."

    if "forgot password" in q:
        return "Use Forgot Password on the login page — we'll send an OTP to your email."

    if "contact" in q or "support" in q:
        return "Email support@moviemind.com or use the Contact page."

    return None


def _answer_catalog_questions(prompt: str) -> str | None:
    q = prompt.lower()
    try:
        with engine.connect() as conn:
            if any(
                k in q
                for k in [
                    "top rated",
                    "best movie",
                    "highest rated",
                    "top movies",
                    "fan favourite",
                ]
            ):
                df = pd.read_sql(
                    text(
                        """
                        SELECT title, vote_average
                        FROM movies
                        WHERE COALESCE(is_approved, 1) = 1
                        ORDER BY vote_average DESC, vote_count DESC
                        LIMIT 6
                        """
                    ),
                    conn,
                )
                return _human_catalog_top(df)

            if any(k in q for k in ["latest", "new release", "newest", "recent"]):
                df = pd.read_sql(
                    text(
                        """
                        SELECT title, release_date
                        FROM movies
                        WHERE release_date IS NOT NULL
                          AND COALESCE(is_approved, 1) = 1
                        ORDER BY release_date DESC
                        LIMIT 6
                        """
                    ),
                    conn,
                )
                return _human_catalog_latest(df)

            if "bollywood" in q and "romance" in q:
                df = pd.read_sql(
                    text(
                        """
                        SELECT title, vote_average
                        FROM movies
                        WHERE COALESCE(is_approved, 1) = 1
                          AND industry LIKE '%Bollywood%'
                        ORDER BY vote_average DESC
                        LIMIT 6
                        """
                    ),
                    conn,
                )
                if not df.empty:
                    return _human_catalog_top(df)

            if "action" in q:
                df = pd.read_sql(
                    text(
                        """
                        SELECT m.title, m.vote_average
                        FROM movies m
                        JOIN movie_genres mg ON m.movie_id = mg.movie_id
                        JOIN genres g ON g.genre_id = mg.genre_id
                        WHERE COALESCE(m.is_approved, 1) = 1
                          AND (g.genre_name LIKE '%Action%' OR g.name LIKE '%Action%')
                        ORDER BY m.vote_average DESC
                        LIMIT 6
                        """
                    ),
                    conn,
                )
                if not df.empty:
                    return _human_catalog_top(df)
    except Exception:
        pass
    return None


def _answer_with_openai(prompt: str, username: str | None) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)
    user_line = f"[User: {username}] {prompt}" if username else prompt

    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_line},
            ],
            max_tokens=500,
            temperature=0.8,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return None


def _generate_reply(prompt: str, username: str | None) -> str:
    q = prompt.strip()
    if not q:
        return "Type a message or tap a quick prompt — I'm ready when you are!"

    answer = _answer_website_questions(q, username)
    if answer:
        return answer

    answer = _answer_catalog_questions(q)
    if answer:
        return answer

    answer = _answer_with_openai(q, username)
    if answer:
        return answer

    picks = []
    try:
        picks = recommend(q) or []
    except Exception:
        picks = []

    if not picks:
        picks = _db_search_movies(q)

    if picks:
        return _human_recommendations(q, picks)

    if any(w in q.lower() for w in ["bored", "surprise", "random", "anything"]):
        try:
            with engine.connect() as conn:
                df = pd.read_sql(
                    text(
                        """
                        SELECT movie_id, title, vote_average, poster_path
                        FROM movies
                        WHERE COALESCE(is_approved, 1) = 1
                        ORDER BY RAND()
                        LIMIT 5
                        """
                    ),
                    conn,
                )
            if not df.empty:
                picks = [
                    {
                        "id": int(r["movie_id"]),
                        "title": r["title"],
                        "rating": float(r["vote_average"] or 0),
                    }
                    for _, r in df.iterrows()
                ]
                return (
                    "Feeling adventurous? Here are random picks from our catalog:\n\n"
                    + _human_recommendations(q, picks)
                )
        except Exception:
            pass

    return (
        "I'm not sure yet — try a genre (action, romance), industry (Bollywood), "
        "'top rated', or a movie title you enjoyed."
    )


def _load_history(user_id: int, limit: int = 40) -> list[dict]:
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text(
                    """
                    SELECT query, response, timestamp
                    FROM chat_logs
                    WHERE user_id = :uid
                    ORDER BY timestamp ASC
                    LIMIT :lim
                    """
                ),
                conn,
                params={"uid": user_id, "lim": limit},
            )
        return df.to_dict("records") if not df.empty else []
    except Exception:
        return []


def _save_turn(user_id: int, query: str, response: str):
    try:
        ensure_schema()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO chat_logs (user_id, query, response)
                    VALUES (:uid, :q, :r)
                    """
                ),
                {"uid": user_id, "q": query[:2000], "r": response[:8000]},
            )
    except Exception:
        pass


def _append_message(user_id: int, user_msg: str, username: str | None):
    from datetime import datetime

    session_key = f"chat_live_{user_id}"
    if session_key not in st.session_state:
        st.session_state[session_key] = _load_history(user_id)

    bot_msg = _generate_reply(user_msg, username)
    turn = {
        "query": user_msg,
        "response": bot_msg,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state[session_key].append(turn)
    _save_turn(user_id, user_msg, bot_msg)


def render_movie_chatbot(user_id: int, username: str | None = None):
    st.subheader("MovieMind Assistant")
    st.caption("Ask anything — tap a quick prompt or type below and press Send.")

    session_key = f"chat_live_{user_id}"
    if session_key not in st.session_state:
        st.session_state[session_key] = _load_history(user_id)

    auto_key = f"chat_auto_send_{user_id}"
    if auto_key in st.session_state and st.session_state[auto_key]:
        msg = st.session_state.pop(auto_key)
        _append_message(user_id, msg, username)
        st.rerun()

    st.markdown(
        """
        <style>
        .mm-chat-wrap {
            height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: var(--mm-chat-wrap-bg) !important;
            border-radius: 12px;
            padding: 14px;
            border: 1px solid var(--mm-chat-border);
            margin-bottom: 12px;
        }
        .mm-chat-user {
            align-self: flex-end;
            max-width: 80%;
            background: var(--mm-chat-user-bg) !important;
            color: var(--mm-chat-user-text) !important;
            padding: 10px 14px;
            border-radius: 14px 14px 4px 14px;
            line-height: 1.45;
        }
        .mm-chat-bot {
            align-self: flex-start;
            max-width: 85%;
            background: var(--mm-chat-bot-bg) !important;
            color: var(--mm-chat-bot-text) !important;
            padding: 10px 14px;
            border-radius: 14px 14px 14px 4px;
            border: 1px solid var(--mm-chat-border);
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    messages = st.session_state[session_key]
    blocks = ['<div class="mm-chat-wrap">']
    if not messages:
        blocks.append(f'<div class="mm-chat-bot">{_esc(_human_greeting(username))}</div>')
    else:
        for m in messages:
            blocks.append(f'<div class="mm-chat-user">{_esc(m.get("query", ""))}</div>')
            blocks.append(f'<div class="mm-chat-bot">{_esc(m.get("response", ""))}</div>')
    blocks.append("</div>")
    st.markdown("".join(blocks), unsafe_allow_html=True)

    st.markdown("**Quick prompts**")
    qcols = st.columns(3, gap="small")
    for i, qp in enumerate(QUICK_PROMPTS):
        with qcols[i % 3]:
            if st.button(qp, key=f"chat_quick_{user_id}_{i}", use_container_width=True):
                st.session_state[auto_key] = qp
                st.rerun()

    with st.form(f"chat_form_{user_id}", clear_on_submit=True):
        prompt = st.text_input(
            "Message",
            placeholder="e.g. thriller like Se7en, or top rated Bollywood…",
            label_visibility="collapsed",
        )
        sent = st.form_submit_button("Send", use_container_width=True)

    if sent:
        if prompt and prompt.strip():
            _append_message(user_id, prompt.strip(), username)
            st.rerun()
        else:
            st.warning("Please type a message first.")
