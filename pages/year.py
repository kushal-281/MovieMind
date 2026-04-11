import streamlit as st
import pandas as pd
from sqlalchemy import text

from components.browse_grid import render_movie_grid
from components.header import show_header
from config.database import engine

st.set_page_config(layout="wide")

show_header()

st.title("📅 Browse by release year")

PAGE = 50
k_sel = "browse_year_value"
k_off = "browse_year_offset"
k_rows = "browse_year_rows"

with engine.connect() as conn:
    years = pd.read_sql(
        text(
            """
            SELECT DISTINCT YEAR(release_date) AS y
            FROM movies
            WHERE release_date IS NOT NULL
            ORDER BY y DESC
            """
        ),
        conn,
    )

if years.empty or years["y"].isna().all():
    st.warning("No release years found in the database.")
    st.stop()

year_list = [int(x) for x in years["y"].dropna().tolist()]

def _reset_offset():
    st.session_state[k_off] = 0
    st.session_state[k_rows] = []

sel = st.selectbox(
    "Select year",
    options=year_list,
    key=k_sel,
    on_change=_reset_offset,
)

off = int(st.session_state.get(k_off, 0))

q_movies = text(
    """
    SELECT movie_id, title, poster_path, vote_average, vote_count, industry
    FROM movies
    WHERE YEAR(release_date) = :yr
    ORDER BY popularity DESC
    LIMIT :lim OFFSET :off
    """
)

with engine.connect() as conn:
    df = pd.read_sql(
        q_movies, conn, params={"yr": int(sel), "lim": PAGE, "off": off}
    )

batch_rows = df.to_dict("records")
if off == 0:
    st.session_state[k_rows] = batch_rows
else:
    existing = st.session_state.get(k_rows, [])
    st.session_state[k_rows] = existing + batch_rows
rows = st.session_state.get(k_rows, [])
st.caption(f"Showing {len(rows)} movies for **{sel}**.")

render_movie_grid(rows, page_key_prefix="year")

if len(batch_rows) == PAGE:
    if st.button("Show more movies", key="year_more"):
        st.session_state[k_off] = off + PAGE
        st.rerun()
