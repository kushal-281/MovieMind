from ml.similarity_model import get_similar_movies

import pandas as pd
from sqlalchemy import text

from config.database import engine
from components.movie_db import APPROVED_WHERE


def recommend(query):
    movies = get_similar_movies(query)
    result = []

    for movie in movies:
        movie_id = movie["movie_id"] if "movie_id" in movie else movie.get("movie_id")

        sql = text(
            """
            SELECT title, vote_average, poster_path
            FROM movies
            WHERE movie_id = :mid AND """ + APPROVED_WHERE + """
            """
        )

        df = pd.read_sql(sql, engine, params={"mid": int(movie_id)})

        if not df.empty:
            row = df.iloc[0]

            result.append(
                {
                    "id": int(movie_id),
                    "title": row["title"],
                    "rating": row["vote_average"],
                    "poster": row["poster_path"],
                }
            )

    return result


def search_movies(query: str, limit: int = 24) -> list[dict]:
    """Search approved movies in DB by title, overview, industry, actor, genre."""
    q = (query or "").strip()
    if not q:
        return []

    pattern = f"%{q}%"
    sql = text(
        f"""
        SELECT DISTINCT m.movie_id, m.title, m.vote_average, m.poster_path
        FROM movies m
        LEFT JOIN movie_actors ma ON ma.movie_id = m.movie_id
        LEFT JOIN actors a ON a.actor_id = ma.actor_id
        LEFT JOIN movie_genres mg ON mg.movie_id = m.movie_id
        LEFT JOIN genres g ON g.genre_id = mg.genre_id
        WHERE {APPROVED_WHERE.replace("is_approved", "m.is_approved")}
          AND (
            m.title LIKE :pat
            OR m.overview LIKE :pat
            OR m.industry LIKE :pat
            OR a.name LIKE :pat
            OR g.genre_name LIKE :pat
            OR g.name LIKE :pat
          )
        ORDER BY m.popularity DESC
        LIMIT :lim
        """
    )
    try:
        df = pd.read_sql(sql, engine, params={"pat": pattern, "lim": limit})
    except Exception:
        try:
            sql2 = text(
                f"""
                SELECT movie_id, title, vote_average, poster_path
                FROM movies
                WHERE {APPROVED_WHERE}
                  AND (title LIKE :pat OR overview LIKE :pat OR industry LIKE :pat)
                ORDER BY popularity DESC
                LIMIT :lim
                """
            )
            df = pd.read_sql(sql2, engine, params={"pat": pattern, "lim": limit})
        except Exception:
            return []

    if df.empty:
        return []

    out = []
    seen = set()
    for _, row in df.iterrows():
        mid = int(row["movie_id"])
        if mid in seen:
            continue
        seen.add(mid)
        out.append(
            {
                "id": mid,
                "title": row["title"],
                "rating": float(row["vote_average"] or 0),
                "poster": row.get("poster_path") or "",
            }
        )
    return out


def get_movie_details(movie_id):
    try:
        mid = int(movie_id)
    except (TypeError, ValueError):
        return None

    import streamlit as st

    admin_view = False
    try:
        u = st.session_state.get("user")
        admin_view = bool(u and u.get("role") == "admin")
    except Exception:
        pass

    if admin_view:
        sql = text("SELECT * FROM movies WHERE movie_id = :mid LIMIT 1")
    else:
        sql = text(
            f"SELECT * FROM movies WHERE movie_id = :mid AND {APPROVED_WHERE} LIMIT 1"
        )
    df = pd.read_sql(sql, engine, params={"mid": mid})
    if df.empty:
        return None

    row = df.iloc[0].to_dict()

    genre_list = []
    try:
        gsql = text(
            """
            SELECT g.genre_name
            FROM genres g
            INNER JOIN movie_genres mg ON g.genre_id = mg.genre_id
            WHERE mg.movie_id = :mid
            ORDER BY g.genre_name
            """
        )
        gdf = pd.read_sql(gsql, engine, params={"mid": mid})
        genre_list = gdf["genre_name"].dropna().tolist()
    except Exception:
        try:
            gsql = text(
                """
                SELECT g.name AS genre_name
                FROM genres g
                INNER JOIN movie_genres mg ON g.genre_id = mg.genre_id
                WHERE mg.movie_id = :mid
                ORDER BY g.name
                """
            )
            gdf = pd.read_sql(gsql, engine, params={"mid": mid})
            genre_list = gdf["genre_name"].dropna().tolist()
        except Exception:
            genre_list = []

    def _fnum(key, default=0):
        v = row.get(key)
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return default
        return v

    poster = row.get("poster_path") or ""
    backdrop = row.get("backdrop_path") or ""

    return {
        "id": row.get("movie_id"),
        "title": row.get("title") or "No Title",
        "original_title": row.get("original_title") or "",
        "overview": row.get("overview") or "",
        "release_date": str(row["release_date"])
        if row.get("release_date") is not None
        else "N/A",
        "poster": poster if isinstance(poster, str) else "",
        "backdrop": backdrop if isinstance(backdrop, str) else "",
        "rating": float(_fnum("vote_average", 0)),
        "vote_count": int(_fnum("vote_count", 0)),
        "popularity": float(_fnum("popularity", 0)),
        "industry": row.get("industry") or "N/A",
        "language": row.get("original_language") or "N/A",
        "genres": genre_list,
    }
