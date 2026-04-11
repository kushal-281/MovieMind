"""Shared movie poster grid (5 per row) with links to movie_detail."""

import streamlit as st

TMDB_IMG = "https://image.tmdb.org/t/p/w500"


def render_movie_grid(movies, page_key_prefix: str = "grid"):
    """
    movies: iterable of dicts with keys movie_id, title, poster_path, vote_average (optional).
    """
    rows = list(movies)
    if not rows:
        st.info("No movies to show.")
        return

    for i in range(0, len(rows), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j >= len(rows):
                break
            m = rows[i + j]
            mid = m.get("movie_id")
            title = m.get("title") or "—"
            poster = m.get("poster_path") or ""
            rating = m.get("vote_average")
            if rating is None:
                rating = 0

            poster_url = (
                TMDB_IMG + poster if poster and not str(poster).startswith("http") else str(poster or "")
            )

            with cols[j]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.caption("No poster")

                st.markdown(
                    f"<p style='text-align:center;font-weight:600;margin:2px 0 0 0;'>{title}</p>",
                    unsafe_allow_html=True,
                )
                if float(rating) >= 7.5:
                    clr = "green"
                elif float(rating) >= 5:
                    clr = "orange"
                else:
                    clr = "red"
                st.markdown(
                    f"<p style='text-align:center;color:{clr};margin:0 0 6px 0;'>⭐ {rating}</p>",
                    unsafe_allow_html=True,
                )

                btn_key = f"{page_key_prefix}_m_{mid}_{i}_{j}"
                if st.button("Movie details", key=btn_key, use_container_width=True):
                    st.query_params["id"] = str(mid)
                    st.switch_page("pages/movie_detail.py")
