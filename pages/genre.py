import streamlit as st
import pandas as pd
from sqlalchemy import text

from components.browse_grid import render_movie_grid
from components.header import show_header
from config.database import engine

st.set_page_config(layout="wide")

show_header()

st.title("🎭 Browse by genre")

PAGE = 50
k_sel = "browse_genre_id"
k_off = "browse_genre_offset"
k_rows = "browse_genre_rows"

with engine.connect() as conn:
    try:
        genres = pd.read_sql(
            text(
                """
                SELECT genre_id, genre_name
                FROM genres
                ORDER BY genre_name
                """
            ),
            conn,
        )
    except Exception:
        genres = pd.read_sql(
            text(
                """
                SELECT genre_id, name AS genre_name
                FROM genres
                ORDER BY name
                """
            ),
            conn,
        )

if genres.empty:
    st.warning("No genres found in the database.")
    st.stop()

labels = [f"{r['genre_name']} (id {r['genre_id']})" for _, r in genres.iterrows()]
id_by_label = {labels[i]: int(genres.iloc[i]["genre_id"]) for i in range(len(labels))}


def _reset_offset():
    st.session_state[k_off] = 0
    st.session_state[k_rows] = []


label = st.selectbox("Select genre", options=labels, key=k_sel, on_change=_reset_offset)
gid = id_by_label[label]
off = int(st.session_state.get(k_off, 0))

q_movies = text(
    """
      SELECT m.movie_id, m.title, m.poster_path, m.vote_average, m.vote_count, m.industry
      FROM movies m
      INNER JOIN movie_genres mg ON m.movie_id = mg.movie_id
      WHERE mg.genre_id = :gid
      ORDER BY m.popularity DESC
      LIMIT :lim OFFSET :off
    """
)

with engine.connect() as conn:
    df = pd.read_sql(q_movies, conn, params={"gid": gid, "lim": PAGE, "off": off})

batch_rows = df.to_dict("records")
if off == 0:
    st.session_state[k_rows] = batch_rows
else:
    existing = st.session_state.get(k_rows, [])
    st.session_state[k_rows] = existing + batch_rows
rows = st.session_state.get(k_rows, [])
st.caption(f"Showing {len(rows)} movies for **{label.split(' (')[0]}**.")

render_movie_grid(rows, page_key_prefix="genre")

if len(batch_rows) == PAGE:
    if st.button("Show more movies", key="genre_more"):
        st.session_state[k_off] = off + PAGE
        st.rerun()
