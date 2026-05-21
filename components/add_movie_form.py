"""Shared add-movie form for profile (user) and admin dashboard."""

from datetime import date

import streamlit as st

from components.movie_db import (
    INDUSTRIES,
    LANGUAGES,
    list_actors,
    list_genres,
    movie_exists_by_title,
    resolve_actor,
    resolve_genre,
    submit_movie,
)


def _norm_path(p: str) -> str:
    p = (p or "").strip()
    if not p:
        return ""
    if "image.tmdb.org" in p and "/t/p/" in p:
        return "/" + p.split("/t/p/")[-1].split("/", 1)[-1]
    return p


def _build_labels(items: list[tuple[int, str]], include_none: bool = False) -> dict[str, str]:
    labels = {str(i): n for i, n in items}
    labels["__other__"] = "➕ Other (add new)"
    if include_none:
        labels["__none__"] = "— None (optional)"
    return labels


def _render_pick(
    label: str,
    labels: dict[str, str],
    key: str,
    *,
    required: bool = False,
) -> tuple[str, str]:
    options = list(labels.keys())
    if not required and "__none__" not in labels:
        options = ["__none__"] + options
        labels = {**labels, "__none__": "— None (optional)"}

    pick = st.selectbox(
        label,
        options=options,
        format_func=lambda k: labels.get(k, k),
        key=key,
    )
    new_name = ""
    if pick == "__other__":
        new_name = st.text_input(f"New name for {label}", key=f"{key}_new")
    return pick, new_name


def _collect_ids(picks: list[tuple[str, str]], resolver) -> list[int]:
    ids = []
    seen = set()
    for pick, new_name in picks:
        if pick in ("", "__none__", None):
            continue
        rid = resolver(pick, new_name)
        if rid and rid not in seen:
            seen.add(rid)
            ids.append(rid)
    return ids


def render_add_movie_form(
    user_id: int,
    *,
    auto_approve: bool = False,
    form_key: str = "add_movie",
):
    """
    auto_approve=True: admin submissions go live immediately.
    """
    st.subheader("➕ Add a movie")
    if auto_approve:
        st.caption("Admin add — movie will be visible on the site right away.")
    else:
        st.caption(
            "Submit a missing title. An admin will review it before it appears publicly."
        )

    genres = list_genres()
    actors = list_actors()
    genre_labels = _build_labels(genres)
    genre_opt = {**genre_labels, "__none__": "— None (optional)"}
    actor_req = _build_labels(actors)
    actor_opt = _build_labels(actors, include_none=True)

    with st.form(form_key, clear_on_submit=False):
        title = st.text_input("Title *")
        original_title = st.text_input("Original title")
        overview = st.text_area("Overview / plot *", height=120)

        c1, c2 = st.columns(2)
        with c1:
            release_date = st.date_input("Release date", value=date.today())
            industry = st.selectbox("Category / Industry *", INDUSTRIES)
            if industry == "Other":
                industry = st.text_input("Custom industry", key=f"{form_key}_ind")
        with c2:
            language = st.selectbox("Original language", LANGUAGES, key=f"{form_key}_lang")
            if language == "other":
                language = st.text_input("Custom language", key=f"{form_key}_clang")
            adult = st.checkbox("Adult content (18+)")
            video = st.checkbox("Has video trailer flag")

        c3, c4 = st.columns(2)
        with c3:
            vote_average = st.number_input(
                "Rating (0–10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1
            )
            vote_count = st.number_input("Vote count", min_value=0, value=1, step=1)
        with c4:
            popularity = st.number_input("Popularity", min_value=0.0, value=1.0, step=0.1)

        poster_path = st.text_input("Poster path or URL")
        backdrop_path = st.text_input("Backdrop path or URL (optional)")

        st.markdown("**Genres** *(1 required, 2 optional)*")
        g1_pick, g1_new = _render_pick(
            "Genre 1 *", genre_labels, f"{form_key}_g1", required=True
        )
        g2_pick, g2_new = _render_pick(
            "Genre 2 (optional)", genre_opt, f"{form_key}_g2"
        )
        g3_pick, g3_new = _render_pick(
            "Genre 3 (optional)", genre_opt, f"{form_key}_g3"
        )

        st.markdown("**Cast** *(1 actor required, 2 optional)*")
        a1_pick, a1_new = _render_pick(
            "Actor 1 *", actor_req, f"{form_key}_a1", required=True
        )
        a2_pick, a2_new = _render_pick(
            "Actor 2 (optional)", actor_opt, f"{form_key}_a2"
        )
        a3_pick, a3_new = _render_pick(
            "Actor 3 (optional)", actor_opt, f"{form_key}_a3"
        )

        btn_label = (
            "Add movie to site" if auto_approve else "Submit for admin review"
        )
        submitted = st.form_submit_button(btn_label, use_container_width=True)

    if not submitted:
        return

    if not title.strip():
        st.error("Title is required.")
        return
    if not overview.strip():
        st.error("Overview is required.")
        return
    if g1_pick in ("__none__", "", None):
        st.error("Genre 1 is required.")
        return
    if a1_pick in ("__none__", "", None):
        st.error("Actor 1 is required.")
        return

    existing = movie_exists_by_title(title)
    if existing:
        st.error(f"This movie already exists: **{existing['title']}** (ID {existing['movie_id']}).")
        return

    genre_ids = _collect_ids(
        [(g1_pick, g1_new), (g2_pick, g2_new), (g3_pick, g3_new)],
        resolve_genre,
    )
    actor_ids = _collect_ids(
        [(a1_pick, a1_new), (a2_pick, a2_new), (a3_pick, a3_new)],
        resolve_actor,
    )

    if not genre_ids:
        st.error("Could not resolve genre 1. Pick a genre or enter a new name.")
        return
    if not actor_ids:
        st.error("Could not resolve actor 1. Pick an actor or enter a new name.")
        return

    data = {
        "title": title.strip(),
        "original_title": (original_title or title).strip(),
        "original_language": (language or "en")[:10],
        "overview": overview.strip(),
        "release_date": release_date,
        "adult": adult,
        "video": video,
        "poster_path": _norm_path(poster_path),
        "backdrop_path": _norm_path(backdrop_path),
        "vote_average": vote_average,
        "vote_count": int(vote_count),
        "popularity": popularity,
        "industry": (industry or "Other").strip()[:50],
    }
    try:
        mid = submit_movie(
            int(user_id),
            data,
            genre_ids,
            actor_ids,
            auto_approve=auto_approve,
        )
        if auto_approve:
            st.success(f"Movie added and published (ID {mid}).")
        else:
            st.success(
                f"Movie submitted (ID {mid}). You'll see it after admin approval."
            )
    except Exception as e:
        st.error(f"Could not save movie: {e}")
