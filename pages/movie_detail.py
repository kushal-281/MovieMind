import streamlit as st

from components.auth import track_movie_dwell
from components.header import show_header
from ml.recommendation_engine import get_movie_details

st.set_page_config(layout="wide")

if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

show_header()

params = st.query_params
movie_id = params.get("id", None)
if isinstance(movie_id, list):
    movie_id = movie_id[0] if movie_id else None
elif isinstance(movie_id, str):
    movie_id = movie_id.strip()

if not movie_id and st.session_state.get("selected_movie_id"):
    movie_id = st.session_state.get("selected_movie_id")

if not movie_id:
    st.warning("No movie selected.")
    st.stop()

movie_id_str = str(movie_id)
if not movie_id_str.startswith("temp_"):
    try:
        track_movie_dwell(int(movie_id_str))
    except ValueError:
        pass

movie = get_movie_details(movie_id)

if not movie:
    st.warning("Movie not found in the database.")
    st.stop()

rating = float(movie.get("rating") or 0)
if rating >= 7.5:
    color = "green"
elif rating >= 5:
    color = "orange"
else:
    color = "red"

hero = None
if movie.get("backdrop"):
    hero = "https://image.tmdb.org/t/p/w1280" + str(movie["backdrop"])
elif movie.get("poster"):
    hero = "https://image.tmdb.org/t/p/w780" + str(movie["poster"])

if hero:
    st.markdown(
        f"""
    <div style="border-radius:12px; overflow:hidden; margin-bottom:1rem;">
        <img src="{hero}" style="width:100%; max-height:320px; object-fit:cover; opacity:0.95;" />
    </div>
    """,
        unsafe_allow_html=True,
    )

left, right = st.columns([1, 2])

with left:
    if movie.get("poster"):
        st.image(
            "https://image.tmdb.org/t/p/w500" + movie["poster"],
            use_container_width=True,
        )

with right:
    st.markdown(f"# {movie.get('title', 'Movie')}")
    if movie.get("original_title") and movie["original_title"] != movie.get("title"):
        st.caption(f"Original title: {movie['original_title']}")

    st.markdown(
        f"**TMDB rating:** <span style='color:{color}; font-size:1.2rem;'>⭐ {rating:.1f}</span> "
        f"&nbsp;·&nbsp; **Votes:** {movie.get('vote_count', 0):,} "
        f"&nbsp;·&nbsp; **Popularity:** {movie.get('popularity', 0):.2f}",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"**Release:** {movie.get('release_date', 'N/A')}  "
        f"&nbsp;|&nbsp; **Industry:** {movie.get('industry', 'N/A')}  "
        f"&nbsp;|&nbsp; **Language:** {movie.get('language', 'N/A')}"
    )

    genres = movie.get("genres") or []
    if genres:
        st.markdown("**Genres:** " + ", ".join(genres))

st.divider()
st.markdown("### Overview")
st.write(movie.get("overview") or "No overview available.")
