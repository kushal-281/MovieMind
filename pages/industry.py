import streamlit as st
import pandas as pd
from sqlalchemy import text

from components.browse_grid import render_movie_grid
from components.header import show_header
from config.database import engine

st.set_page_config(layout="wide")

show_header()

st.title("🎬 Browse by industry")

PAGE = 50
k_sel = "browse_industry_value"
k_off = "browse_industry_offset"
k_rows = "browse_industry_rows"

with engine.connect() as conn:
    inds = pd.read_sql(
        text(
            """
            SELECT DISTINCT industry
            FROM movies
            WHERE industry IS NOT NULL AND TRIM(industry) <> ''
            ORDER BY industry
            """
        ),
        conn,
    )

if inds.empty:
    st.warning("No industries found in the database.")
    st.stop()

industry_list = inds["industry"].tolist()


def _reset_offset():
    st.session_state[k_off] = 0
    st.session_state[k_rows] = []


sel = st.selectbox(
    "Select industry (Hollywood, Bollywood, …)",
    options=industry_list,
    key=k_sel,
    on_change=_reset_offset,
)

off = int(st.session_state.get(k_off, 0))

q_movies = text(
    """
    SELECT movie_id, title, poster_path, vote_average, vote_count, industry
    FROM movies
    WHERE industry = :ind
    ORDER BY popularity DESC
    LIMIT :lim OFFSET :off
    """
)

with engine.connect() as conn:
    df = pd.read_sql(
        q_movies, conn, params={"ind": sel, "lim": PAGE, "off": off}
    )

batch_rows = df.to_dict("records")
if off == 0:
    st.session_state[k_rows] = batch_rows
else:
    existing = st.session_state.get(k_rows, [])
    st.session_state[k_rows] = existing + batch_rows
rows = st.session_state.get(k_rows, [])
st.caption(f"Showing {len(rows)} movies in **{sel}**.")

render_movie_grid(rows, page_key_prefix="ind", show_row_dividers=True)

if len(batch_rows) == PAGE:
    if st.button("Show more movies", key="ind_more"):
        st.session_state[k_off] = off + PAGE
        st.rerun()
