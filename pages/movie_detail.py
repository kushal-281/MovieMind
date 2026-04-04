import streamlit as st
from components.header import show_header

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

# ---------------- HEADER ----------------
show_header()

# ---------------- GET PARAM ----------------
params = st.query_params
movie_id = params.get("id", None)

if not movie_id:
    st.warning("No movie selected.")
    st.stop()

# ---------------- IMPORT ----------------
from ml.recommendation_engine import get_movie_details

# ---------------- FETCH ----------------
movie = get_movie_details(movie_id)

if not movie:
    st.warning("Movie not found")

else:
    # Poster
    st.image(
        "https://image.tmdb.org/t/p/w500" + movie.get("poster", ""),
        use_container_width=True
    )

    # Title
    st.markdown(f"## {movie.get('title', 'No Title')}")

    # Rating
    rating = movie.get("rating", 0)
    if rating >= 7.5:
        color = "green"
    elif rating >= 5:
        color = "orange"
    else:
        color = "red"

    st.markdown(
        f"**Rating:** <span style='color:{color}'>⭐ {rating}</span>",
        unsafe_allow_html=True
    )

    st.markdown(f"**Overview:** {movie.get('overview', 'No Overview')}")
    st.markdown(f"**Release Date:** {movie.get('release_date', 'N/A')}")
    st.markdown(f"**Genres:** {', '.join(movie.get('genres', []))}")