"""Movie visibility, user submissions, and reviews."""

from datetime import date, datetime

import pandas as pd
from sqlalchemy import text

from config.database import engine, ensure_schema

# Only approved movies appear on the public site (NULL treated as approved for legacy rows).
APPROVED_WHERE = "COALESCE(is_approved, 1) = 1"
APPROVED_WHERE_M = "COALESCE(m.is_approved, 1) = 1"

USER_MOVIE_ID_START = 1_000_000_000
USER_ACTOR_ID_START = 1_000_000_000

INDUSTRIES = ["Hollywood", "Bollywood", "Tollywood", "Other"]
LANGUAGES = ["en", "hi", "te", "ta", "ml", "kn", "bn", "mr", "other"]


def _conn():
    ensure_schema()
    return engine.connect()


def movie_exists_by_title(title: str) -> dict | None:
    t = (title or "").strip()
    if not t:
        return None
    with _conn() as conn:
        row = conn.execute(
            text(
                """
                SELECT movie_id, title, COALESCE(is_approved, 1) AS is_approved
                FROM movies
                WHERE LOWER(TRIM(title)) = LOWER(:t)
                LIMIT 1
                """
            ),
            {"t": t},
        ).fetchone()
    if not row:
        return None
    return {
        "movie_id": int(row[0]),
        "title": row[1],
        "is_approved": bool(int(row[2])),
    }


def next_user_movie_id() -> int:
    with _conn() as conn:
        row = conn.execute(
            text(
                """
                SELECT COALESCE(MAX(movie_id), :start - 1) + 1
                FROM movies
                WHERE movie_id >= :start
                """
            ),
            {"start": USER_MOVIE_ID_START},
        ).fetchone()
    return int(row[0])


def next_user_actor_id() -> int:
    with _conn() as conn:
        row = conn.execute(
            text(
                """
                SELECT COALESCE(MAX(actor_id), :start - 1) + 1
                FROM actors
                WHERE actor_id >= :start
                """
            ),
            {"start": USER_ACTOR_ID_START},
        ).fetchone()
    return int(row[0])


def next_user_genre_id() -> int:
    with _conn() as conn:
        row = conn.execute(
            text(
                """
                SELECT COALESCE(MAX(genre_id), :start - 1) + 1
                FROM genres
                WHERE genre_id >= :start
                """
            ),
            {"start": USER_ACTOR_ID_START},
        ).fetchone()
    return int(row[0])


def list_genres() -> list[tuple[int, str]]:
    with _conn() as conn:
        try:
            df = pd.read_sql(
                text("SELECT genre_id, genre_name AS name FROM genres ORDER BY genre_name"),
                conn,
            )
        except Exception:
            df = pd.read_sql(
                text("SELECT genre_id, name FROM genres ORDER BY name"),
                conn,
            )
    return [(int(r["genre_id"]), str(r["name"])) for _, r in df.iterrows()]


def list_actors() -> list[tuple[int, str]]:
    with _conn() as conn:
        df = pd.read_sql(
            text("SELECT actor_id, name FROM actors ORDER BY name LIMIT 500"),
            conn,
        )
    return [(int(r["actor_id"]), str(r["name"])) for _, r in df.iterrows()]


def resolve_genre(genre_choice: str, new_genre_name: str) -> int | None:
    if genre_choice == "__other__":
        name = (new_genre_name or "").strip()
        if not name:
            return None
        with engine.begin() as conn:
            existing = None
            try:
                existing = conn.execute(
                    text(
                        """
                        SELECT genre_id FROM genres
                        WHERE LOWER(TRIM(genre_name)) = LOWER(:n)
                        LIMIT 1
                        """
                    ),
                    {"n": name},
                ).fetchone()
            except Exception:
                existing = conn.execute(
                    text(
                        """
                        SELECT genre_id FROM genres
                        WHERE LOWER(TRIM(name)) = LOWER(:n)
                        LIMIT 1
                        """
                    ),
                    {"n": name},
                ).fetchone()
            if existing:
                return int(existing[0])
            new_id = next_user_genre_id()
            try:
                conn.execute(
                    text("INSERT INTO genres (genre_id, genre_name) VALUES (:gid, :n)"),
                    {"gid": new_id, "n": name},
                )
            except Exception:
                conn.execute(
                    text("INSERT INTO genres (genre_id, name) VALUES (:gid, :n)"),
                    {"gid": new_id, "n": name},
                )
            return new_id
    if genre_choice and genre_choice.isdigit():
        return int(genre_choice)
    return None


def resolve_actor(actor_choice: str, new_actor_name: str) -> int | None:
    if actor_choice == "__other__":
        name = (new_actor_name or "").strip()
        if not name:
            return None
        with engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT actor_id FROM actors WHERE LOWER(TRIM(name)) = LOWER(:n) LIMIT 1"
                ),
                {"n": name},
            ).fetchone()
            if row:
                return int(row[0])
            aid = next_user_actor_id()
            conn.execute(
                text("INSERT INTO actors (actor_id, name) VALUES (:aid, :n)"),
                {"aid": aid, "n": name},
            )
            return aid
    if actor_choice and actor_choice.isdigit():
        return int(actor_choice)
    return None


def submit_movie(
    user_id: int,
    data: dict,
    genre_ids: list[int],
    actor_ids: list[int],
    *,
    auto_approve: bool = False,
) -> int:
    mid = next_user_movie_id()
    approved = 1 if auto_approve else 0
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO movies (
                    movie_id, title, original_title, original_language, overview,
                    release_date, adult, backdrop_path, poster_path, popularity,
                    vote_average, vote_count, video, industry,
                    is_approved, submitted_by
                ) VALUES (
                    :movie_id, :title, :original_title, :original_language, :overview,
                    :release_date, :adult, :backdrop_path, :poster_path, :popularity,
                    :vote_average, :vote_count, :video, :industry,
                    :is_approved, :submitted_by
                )
                """
            ),
            {
                "movie_id": mid,
                "title": data["title"],
                "original_title": data.get("original_title") or data["title"],
                "original_language": data.get("original_language") or "en",
                "overview": data.get("overview") or "",
                "release_date": data.get("release_date"),
                "adult": bool(data.get("adult", False)),
                "backdrop_path": data.get("backdrop_path") or "",
                "poster_path": data.get("poster_path") or "",
                "popularity": float(data.get("popularity") or 0),
                "vote_average": float(data.get("vote_average") or 0),
                "vote_count": int(data.get("vote_count") or 0),
                "video": bool(data.get("video", False)),
                "industry": data.get("industry") or "Other",
                "is_approved": approved,
                "submitted_by": int(user_id),
            },
        )
        for gid in genre_ids:
            conn.execute(
                text(
                    "INSERT IGNORE INTO movie_genres (movie_id, genre_id) VALUES (:mid, :gid)"
                ),
                {"mid": mid, "gid": gid},
            )
        for aid in actor_ids:
            conn.execute(
                text(
                    "INSERT INTO movie_actors (movie_id, actor_id) VALUES (:mid, :aid)"
                ),
                {"mid": mid, "aid": aid},
            )
    return mid


def get_pending_movies():
    with _conn() as conn:
        return pd.read_sql(
            text(
                """
                SELECT m.movie_id, m.title, m.industry, m.release_date,
                       m.submitted_by, u.username AS submitted_by_name,
                       m.overview, m.poster_path, m.vote_average
                FROM movies m
                LEFT JOIN users u ON u.user_id = m.submitted_by
                WHERE COALESCE(m.is_approved, 1) = 0
                ORDER BY m.movie_id DESC
                """
            ),
            conn,
        )


def set_movie_approval(movie_id: int, approved: bool):
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE movies SET is_approved = :a WHERE movie_id = :mid"),
            {"a": 1 if approved else 0, "mid": int(movie_id)},
        )
        if approved:
            conn.execute(
                text(
                    """
                    UPDATE movies
                    SET popularity = GREATEST(COALESCE(popularity, 0), 1)
                    WHERE movie_id = :mid
                    """
                ),
                {"mid": int(movie_id)},
            )


def get_movie_reviews(movie_id: int):
    with _conn() as conn:
        return pd.read_sql(
            text(
                """
                SELECT r.rating_id, r.rating, r.review, r.created_at, u.username
                FROM ratings r
                JOIN users u ON u.user_id = r.user_id
                WHERE r.movie_id = :mid AND r.review IS NOT NULL AND TRIM(r.review) <> ''
                ORDER BY r.created_at DESC
                """
            ),
            conn,
            params={"mid": int(movie_id)},
        )


def user_has_review(user_id: int, movie_id: int) -> bool:
    with _conn() as conn:
        row = conn.execute(
            text(
                """
                SELECT rating_id FROM ratings
                WHERE user_id = :uid AND movie_id = :mid
                LIMIT 1
                """
            ),
            {"uid": int(user_id), "mid": int(movie_id)},
        ).fetchone()
    return row is not None


def add_or_update_review(user_id: int, movie_id: int, rating: float, review: str):
    review = (review or "").strip()
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                "SELECT rating_id FROM ratings WHERE user_id = :uid AND movie_id = :mid"
            ),
            {"uid": int(user_id), "mid": int(movie_id)},
        ).fetchone()
        if existing:
            conn.execute(
                text(
                    """
                    UPDATE ratings SET rating = :rating, review = :review
                    WHERE user_id = :uid AND movie_id = :mid
                    """
                ),
                {
                    "rating": float(rating),
                    "review": review,
                    "uid": int(user_id),
                    "mid": int(movie_id),
                },
            )
        else:
            conn.execute(
                text(
                    """
                    INSERT INTO ratings (user_id, movie_id, rating, review)
                    VALUES (:uid, :mid, :rating, :review)
                    """
                ),
                {
                    "uid": int(user_id),
                    "mid": int(movie_id),
                    "rating": float(rating),
                    "review": review,
                },
            )
