import json
import time

import streamlit as st
from sqlalchemy import text

from cookies import cookies
from config.database import engine, ensure_schema


def restore_session():
    """Restore user from cookies so refresh does not log out."""
    if st.session_state.get("force_logout"):
        st.session_state.user = None
        return

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.get("user"):
        return

    raw = cookies.get("user")
    if not raw:
        return
    try:
        user = json.loads(raw)
        if isinstance(user, dict) and user.get("user_id"):
            st.session_state.user = user
    except Exception:
        pass


def track_site_time():
    """Approximate active time on site by summing seconds between Streamlit reruns."""
    ensure_schema()
    user = st.session_state.get("user")
    if not user or not user.get("user_id"):
        return

    now = time.time()
    last = st.session_state.get("_last_site_ping_ts")
    st.session_state["_last_site_ping_ts"] = now
    if last is None:
        return

    delta = int(now - last)
    if delta <= 0 or delta > 600:
        return

    user_id = int(user["user_id"])
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE users SET total_site_seconds = COALESCE(total_site_seconds, 0) + :d "
                    "WHERE user_id = :uid"
                ),
                {"d": delta, "uid": user_id},
            )
    except Exception:
        pass


def track_movie_dwell(movie_id: int):
    """Accumulate seconds spent on a movie detail page (between reruns)."""
    user = st.session_state.get("user")
    if not user or not user.get("user_id") or not movie_id:
        return

    now = time.time()
    key = f"_movie_dwell_{movie_id}"
    last = st.session_state.get(key)
    st.session_state[key] = now
    if last is None:
        return

    delta = int(now - last)
    if delta <= 0 or delta > 600:
        return

    user_id = int(user["user_id"])
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT activity_id, time_spent FROM user_activity "
                    "WHERE user_id = :uid AND movie_id = :mid LIMIT 1"
                ),
                {"uid": user_id, "mid": movie_id},
            ).fetchone()
            if row:
                conn.execute(
                    text(
                        "UPDATE user_activity SET time_spent = :ts, last_viewed = NOW() "
                        "WHERE activity_id = :aid"
                    ),
                    {"ts": int(row[1] or 0) + delta, "aid": int(row[0])},
                )
            else:
                conn.execute(
                    text(
                        "INSERT INTO user_activity (user_id, movie_id, time_spent, last_viewed) "
                        "VALUES (:uid, :mid, :ts, NOW())"
                    ),
                    {"uid": user_id, "mid": movie_id, "ts": delta},
                )
    except Exception:
        pass


def require_login():
    restore_session()
    if not st.session_state.get("user"):
        st.switch_page("pages/login.py")


def login_user(user_dict):
    if "force_logout" in st.session_state:
        del st.session_state["force_logout"]
    st.session_state.user = user_dict
    cookies["user"] = json.dumps(user_dict)
    cookies.save()
    st.session_state["_last_site_ping_ts"] = time.time()
