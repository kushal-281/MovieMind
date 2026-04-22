import streamlit as st

from components.auth import track_movie_dwell
from components.header import show_header
from components.footer import show_footer
from ml.recommendation_engine import get_movie_details

st.set_page_config(layout="wide")

if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

show_header()

# --- GET MOVIE ID ---
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

# --- TRACK DWELL ---
movie_id_str = str(movie_id)
if not movie_id_str.startswith("temp_"):
    try:
        track_movie_dwell(int(movie_id_str))
    except ValueError:
        pass

# --- FETCH MOVIE ---
movie = get_movie_details(movie_id)

if not movie:
    st.warning("Movie not found in the database.")
    st.stop()

# --- TITLE (CENTER + ITALIC) ---
st.markdown(
    f"<h1 style='text-align:center; font-style:italic;'>{movie.get('title', 'Movie')}</h1>",
    unsafe_allow_html=True
)

if movie.get("original_title") and movie["original_title"] != movie.get("title"):
    st.caption(f"Original title: {movie['original_title']}")

# --- HERO IMAGE ---
hero = None
if movie.get("backdrop"):
    hero = "https://image.tmdb.org/t/p/w1280" + str(movie["backdrop"])
elif movie.get("poster"):
    hero = "https://image.tmdb.org/t/p/w780" + str(movie["poster"])

if hero:
    st.image(hero, use_container_width=True)

# --- MAIN LAYOUT ---
left, right = st.columns([1, 2])

with left:
    if movie.get("poster"):
        st.image(
            "https://image.tmdb.org/t/p/w500" + movie["poster"],
            use_container_width=True,
        )

with right:
    rating = float(movie.get("rating") or 0)

    # --- COLOR LOGIC ---
    if rating >= 7.5:
        rating_text = f"<span style='color:green; font-size:20px;'>⭐ {rating:.1f} (Excellent)</span>"
    elif rating >= 5:
        rating_text = f"<span style='color:orange; font-size:20px;'>⭐ {rating:.1f} (Good)</span>"
    else:
        rating_text = f"<span style='color:red; font-size:20px;'>⭐ {rating:.1f} (Poor)</span>"

    st.markdown(f"**Rating:** {rating_text}", unsafe_allow_html=True)

    st.markdown(f"**Votes:** <span style='color:#00aaff'>{movie.get('vote_count', 0):,}</span>", unsafe_allow_html=True)
    st.markdown(f"**Popularity:** <span style='color:#00aaff'>{movie.get('popularity', 0):.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Release Date:** <span style='color:#00aaff'>{movie.get('release_date', 'N/A')}</span>", unsafe_allow_html=True)
    st.markdown(f"**Industry:** <span style='color:#00aaff'>{movie.get('industry', 'N/A')}</span>", unsafe_allow_html=True)
    st.markdown(f"**Language:** <span style='color:#00aaff'>{movie.get('language', 'N/A')}</span>", unsafe_allow_html=True)

    genres = movie.get("genres") or []
    if genres:
        st.markdown(
            "**Genres:** " + ", ".join([f"<span style='color:#ff4b4b'>{g}</span>" for g in genres]),
            unsafe_allow_html=True
        )

# --- OVERVIEW ---
st.divider()
st.subheader("Overview")
st.write(movie.get("overview") or "No overview available.")

show_footer()