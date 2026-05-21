import streamlit as st

from components.auth import restore_session, track_movie_dwell
from components.footer import show_footer
from components.header import show_header
from components.movie_db import (
    add_or_update_review,
    get_movie_reviews,
    user_has_review,
)
from ml.recommendation_engine import get_movie_details

st.set_page_config(layout="wide")
restore_session()

if "search_movie" not in st.session_state:
    st.session_state["search_movie"] = ""

show_header()

st.markdown(
    """
    <style>
    .mm-overview {
        font-size: 1.03rem;
        line-height: 1.65;
        padding: 2px 0 8px 0;
    }
    .movie-title {
        color: var(--mm-accent) !important;
        text-align: center !important;
        font-style: italic !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    .mm-review-card {
        background: var(--mm-card-bg);
        border: 1px solid var(--mm-border);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .mm-review-user {
        font-weight: 700;
        color: var(--mm-accent);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    st.warning("Movie not found or not yet approved for public viewing.")
    st.stop()

st.markdown(
    f"<h1 class='movie-title'>{movie.get('title', 'Movie')}</h1>",
    unsafe_allow_html=True,
)

if movie.get("original_title") and movie["original_title"] != movie.get("title"):
    st.caption(f"Original title: {movie['original_title']}")

hero = None
if movie.get("backdrop"):
    hero = "https://image.tmdb.org/t/p/w1280" + str(movie["backdrop"])
elif movie.get("poster"):
    hero = "https://image.tmdb.org/t/p/w780" + str(movie["poster"])

if hero:
    st.image(hero, use_container_width=True)

left, right = st.columns([1, 2])

with left:
    if movie.get("poster"):
        st.image(
            "https://image.tmdb.org/t/p/w500" + movie["poster"],
            use_container_width=True,
        )

with right:
    rating = float(movie.get("rating") or 0)
    if rating >= 7.5:
        rating_text = f"<span style='color:#18b56a; font-size:20px;'>⭐ {rating:.1f} (Excellent)</span>"
    elif rating >= 5:
        rating_text = f"<span style='color:#f59e0b; font-size:20px;'>⭐ {rating:.1f} (Good)</span>"
    else:
        rating_text = f"<span style='color:#ef4444; font-size:20px;'>⭐ {rating:.1f} (Poor)</span>"

    st.markdown(f"**Rating:** {rating_text}", unsafe_allow_html=True)
    st.markdown(
        f"**Votes:** <span style='color:var(--mm-accent)'>{movie.get('vote_count', 0):,}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Popularity:** <span style='color:var(--mm-accent)'>{movie.get('popularity', 0):.2f}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Release Date:** <span style='color:var(--mm-accent)'>{movie.get('release_date', 'N/A')}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Industry:** <span style='color:var(--mm-accent)'>{movie.get('industry', 'N/A')}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Language:** <span style='color:var(--mm-accent)'>{movie.get('language', 'N/A')}</span>",
        unsafe_allow_html=True,
    )

    genres = movie.get("genres") or []
    if genres:
        st.markdown(
            "**Genres:** "
            + ", ".join([f"<span style='color:var(--mm-accent)'>{g}</span>" for g in genres]),
            unsafe_allow_html=True,
        )

st.divider()

tab_overview, tab_reviews = st.tabs(["Overview", "Reviews"])

with tab_overview:
    overview = (movie.get("overview") or "").strip()
    if overview:
        st.markdown(
            f"<div class='mm-overview' style='color: var(--mm-text);'>{overview}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No overview available.")

with tab_reviews:
    mid = int(movie.get("id") or movie_id)
    reviews_df = get_movie_reviews(mid)

    if not reviews_df.empty:
        for _, row in reviews_df.iterrows():
            stars = "⭐" * max(1, min(5, int(round(float(row["rating"])))))
            created = row.get("created_at", "")
            st.markdown(
                f"""
                <div class="mm-review-card">
                    <div class="mm-review-user">{row['username']}</div>
                    <div>{stars} ({float(row['rating']):.1f})</div>
                    <p style="margin:8px 0 0 0;">{row['review']}</p>
                    <small style="color:var(--mm-muted);">{created}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No user reviews yet. Be the first to add one below.")

    st.markdown("#### Add your review")
    u = st.session_state.get("user")
    if not u:
        st.warning("Log in to write a review.")
        if st.button("Go to Login", use_container_width=True):
            st.switch_page("pages/login.py")
    else:
        uid = int(u["user_id"])
        already = user_has_review(uid, mid)
        if already:
            st.caption("You already submitted a review for this movie (you can update it below).")

        with st.form("review_form"):
            user_rating = st.slider("Your star rating", 1.0, 5.0, 4.0, 0.5)
            review_text = st.text_area("Your review", height=120, max_chars=2000)
            if st.form_submit_button(
                "Submit review" if not already else "Update review",
                use_container_width=True,
            ):
                if not review_text.strip():
                    st.error("Please write a review.")
                else:
                    try:
                        add_or_update_review(uid, mid, user_rating, review_text)
                        st.success("Review saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not save review: {e}")

show_footer()
