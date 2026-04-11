import streamlit as st
import pandas as pd
from sqlalchemy import text

from config.database import engine
from components.footer import show_footer
from components.browse_grid import render_movie_grid
from components.header import show_header

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
    if st.button("Genre"):
        st.switch_page("pages/genre.py")

with col2:
    st.image("assets/industry.png", use_container_width=True)
    if st.button("Industry"):
        st.switch_page("pages/industry.py")

with col3:
    st.image("assets/year.png", use_container_width=True)
    if st.button("Year"):
        st.switch_page("pages/year.py")

# ---------------- TOP SIMILAR MOVIES (USER HISTORY) ----------------
st.markdown("### Top Similar Movies")
user = st.session_state.get("user")
if user and user.get("user_id"):
    try:
        with engine.connect() as conn:
            hist = pd.read_sql(
                text(
                    """
                    SELECT m.movie_id, m.title, m.poster_path, m.vote_average, m.vote_count, m.industry
                    FROM user_activity ua
                    JOIN movies m ON m.movie_id = ua.movie_id
                    WHERE ua.user_id = :uid
                    ORDER BY ua.time_spent DESC, ua.last_viewed DESC
                    LIMIT 20
                    """
                ),
                conn,
                params={"uid": int(user["user_id"])},
            )
        if hist.empty:
            st.info("Watch a few movies to get personalized similar picks here.")
        else:
            rows = hist.to_dict("records")
            for i in range(0, len(rows), 5):
                render_movie_grid(rows[i : i + 5], page_key_prefix=f"home_sim_{i}")
                st.markdown("<hr>", unsafe_allow_html=True)
    except Exception:
        st.info("Similar movie recommendations are temporarily unavailable.")
else:
    st.info("Login to see top similar movies from your watch history.")

# ---------------- MOVIE CLICK ----------------
if "id" in st.query_params:
    try:
        movie_id = int(st.query_params["id"][0])
        st.query_params.clear()
        st.query_params["id"] = str(movie_id)
        st.switch_page("pages/movie_detail.py")
    except Exception:
        pass


# --
st.text('byeee')
# ---------------- FOOTER ----------------
show_footer()