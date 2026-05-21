import streamlit as st

from components.browse_grid import render_movie_grid
from components.header import SK_SEARCH_MOVIE, show_header
from ml.recommendation_engine import recommend, search_movies

st.set_page_config(layout="wide")

if SK_SEARCH_MOVIE not in st.session_state:
    st.session_state[SK_SEARCH_MOVIE] = ""

show_header()

query = st.session_state.get(SK_SEARCH_MOVIE, "").strip()

st.title("🔎 Search Results")
if query:
    st.markdown(f"Showing matches for **{query}**")
else:
    st.info("Use the search bar above — type a title, actor, or genre, then click **Search**.")

if query:
    results = []
    try:
        results = recommend(query) or []
    except Exception:
        results = []

    if not results:
        results = search_movies(query, limit=30)

    if not results:
        st.warning("No movies found. Try another keyword or a partial title.")
    else:
        rows = []
        seen = set()
        for m in results:
            mid = m.get("id")
            if not mid or mid in seen:
                continue
            try:
                mid = int(mid)
            except (TypeError, ValueError):
                continue
            seen.add(mid)
            rows.append(
                {
                    "movie_id": mid,
                    "title": m.get("title") or "—",
                    "poster_path": m.get("poster") or "",
                    "vote_average": m.get("rating", 0),
                    "vote_count": 0,
                    "industry": "",
                }
            )

        if not rows:
            st.warning("No displayable results.")
        else:
            st.caption(f"Found **{len(rows)}** movie(s).")
            render_movie_grid(rows, page_key_prefix="search", show_row_dividers=True)
