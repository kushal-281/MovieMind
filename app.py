import streamlit as st
import pandas as pd
from sqlalchemy import text

from config.database import engine
from components.footer import show_footer
from components.browse_grid import render_movie_grid
from components.header import show_header
from ml.recommendation_engine import recommend

st.set_page_config(layout="wide")

# ---------------- GLOBAL WIDTH FIX ----------------
st.markdown("""
<style>
.block-container {
    max-width: 1350px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 0rem !important;
}
/* Change this value to adjust button spacing app-wide */
div.stButton > button {
    margin-top: 8px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER (restores session from cookie every rerun) ----------------
show_header()

# # ---------------- MAIN CONTENT ----------------
# st.title("🎬 MovieMind Dashboard")

# if st.session_state.user:
#     st.success(f"Welcome, {st.session_state.user['username']}")

#     if st.session_state.user.get("role") == "admin":
#         st.info("You are logged in as Admin")
#     else:
#         st.info("You are logged in as User")

# else:
#     st.info("Please login to access full features")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("assets/genre.png", use_container_width=True)
    if st.button("Genre", use_container_width=True):
        st.switch_page("pages/genre.py")

with col2:
    st.image("assets/industry.png", use_container_width=True)
    if st.button("Industry", use_container_width=True):
        st.switch_page("pages/industry.py")

with col3:
    st.image("assets/year.png", use_container_width=True)
    if st.button("Year", use_container_width=True):
        st.switch_page("pages/year.py")

# ---------------- TOP SIMILAR MOVIES (USER HISTORY) ----------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Top Similar Movies")
user = st.session_state.get("user")
if user and user.get("user_id"):
    try:
        with engine.connect() as conn:
            hist = pd.read_sql(
                text(
                    """
                    SELECT query
                    FROM search_history
                    WHERE user_id = :uid
                    ORDER BY searched_at DESC
                    LIMIT 5
                    """
                ),
                conn,
                params={"uid": int(user["user_id"])},
            )
        if hist.empty:
            st.info("Watch a few movies to get personalized similar picks here.")
        else:
            rec_rows = []
            seen = set()
            for q in hist["query"].dropna().tolist():
                for m in recommend(str(q).strip())[:8]:
                    mid = m.get("id")
                    if mid in seen or not mid:
                        continue
                    seen.add(mid)
                    rec_rows.append(
                        {
                            "movie_id": int(mid),
                            "title": m.get("title"),
                            "poster_path": m.get("poster"),
                            "vote_average": m.get("rating", 0),
                            "vote_count": 0,
                            "industry": "",
                        }
                    )
                if len(rec_rows) >= 20:
                    break

            if rec_rows:
                render_movie_grid(
                    rec_rows[:20], page_key_prefix="home_sim", show_row_dividers=True
                )
            else:
                st.info("No similar recommendations found from recent searches yet.")
    except Exception:
        st.info("Similar movie recommendations are temporarily unavailable.")
else:
    st.info("Login to see top similar movies from your watch history.")

# ---------------- MOVIE CLICK ----------------
if "id" in st.query_params:
    try:
        raw_mid = st.query_params.get("id")
        if isinstance(raw_mid, list):
            raw_mid = raw_mid[0] if raw_mid else None
        movie_id = int(raw_mid)
        st.session_state["selected_movie_id"] = str(movie_id)
        st.query_params.clear()
        st.query_params["id"] = str(movie_id)
        st.switch_page("pages/movie_detail.py")
    except Exception:
        pass


# ---------------- FOOTER ----------------
show_footer()