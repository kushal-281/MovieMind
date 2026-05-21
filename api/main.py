from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.db import engine


app = FastAPI(title="MovieMind API", version="0.1.0")

# Allow Streamlit (8501) or any local dev origin to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later if you want strict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/movies")
def list_movies(
    q: str | None = Query(default=None, description="Search by title prefix / contains"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    sql = """
        SELECT movie_id, title, original_title, original_language, overview,
               release_date, popularity, vote_average, vote_count, industry,
               poster_path, backdrop_path
        FROM movies
        WHERE (:q IS NULL OR title LIKE CONCAT('%', :q, '%'))
        ORDER BY popularity DESC
        LIMIT :limit OFFSET :offset
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text(sql),
            {"q": (q.strip() if q else None), "limit": int(limit), "offset": int(offset)},
        ).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int) -> dict[str, Any]:
    sql = """
        SELECT movie_id, title, original_title, original_language, overview,
               release_date, popularity, vote_average, vote_count, industry,
               poster_path, backdrop_path
        FROM movies
        WHERE movie_id = :mid
        LIMIT 1
    """
    with engine.connect() as conn:
        row = conn.execute(text(sql), {"mid": int(movie_id)}).mappings().first()
        if not row:
            return {"error": "movie_not_found"}

        genres = conn.execute(
            text(
                """
                SELECT g.genre_id, COALESCE(g.genre_name, g.name) AS name
                FROM movie_genres mg
                JOIN genres g ON g.genre_id = mg.genre_id
                WHERE mg.movie_id = :mid
                ORDER BY name
                """
            ),
            {"mid": int(movie_id)},
        ).mappings().all()

        actors = conn.execute(
            text(
                """
                SELECT a.actor_id, a.name
                FROM movie_actors ma
                JOIN actors a ON a.actor_id = ma.actor_id
                WHERE ma.movie_id = :mid
                ORDER BY a.name
                LIMIT 50
                """
            ),
            {"mid": int(movie_id)},
        ).mappings().all()

    d = dict(row)
    d["genres"] = [dict(g) for g in genres]
    d["actors"] = [dict(a) for a in actors]
    return d


@app.get("/genres")
def list_genres(limit: int = Query(default=200, ge=1, le=500)) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT genre_id, COALESCE(genre_name, name) AS name
                FROM genres
                ORDER BY name
                LIMIT :limit
                """
            ),
            {"limit": int(limit)},
        ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@app.get("/genres/{genre_id}/movies")
def movies_by_genre(
    genre_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT m.movie_id, m.title, m.vote_average, m.vote_count, m.popularity, m.release_date
                FROM movie_genres mg
                JOIN movies m ON m.movie_id = mg.movie_id
                WHERE mg.genre_id = :gid
                ORDER BY m.popularity DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"gid": int(genre_id), "limit": int(limit), "offset": int(offset)},
        ).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}


@app.get("/actors")
def list_actors(
    q: str | None = Query(default=None, description="Search actor name contains"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT actor_id, name, dob, bio
                FROM actors
                WHERE (:q IS NULL OR name LIKE CONCAT('%', :q, '%'))
                ORDER BY name
                LIMIT :limit OFFSET :offset
                """
            ),
            {"q": (q.strip() if q else None), "limit": int(limit), "offset": int(offset)},
        ).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}


@app.get("/actors/{actor_id}/movies")
def movies_by_actor(
    actor_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT m.movie_id, m.title, m.vote_average, m.vote_count, m.popularity, m.release_date
                FROM movie_actors ma
                JOIN movies m ON m.movie_id = ma.movie_id
                WHERE ma.actor_id = :aid
                ORDER BY m.popularity DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"aid": int(actor_id), "limit": int(limit), "offset": int(offset)},
        ).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text

from api.db import engine


app = FastAPI(title="MovieMind API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/movies")
def list_movies(
    q: str | None = Query(default=None, description="Search by title prefix/contains"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    where = ""
    params: dict[str, Any] = {"limit": int(limit), "offset": int(offset)}
    if q and q.strip():
        where = "WHERE title LIKE :q OR original_title LIKE :q"
        params["q"] = f"%{q.strip()}%"

    sql = text(
        f"""
        SELECT movie_id, title, original_title, release_date, vote_average, vote_count, popularity, industry
        FROM movies
        {where}
        ORDER BY popularity DESC, vote_count DESC
        LIMIT :limit OFFSET :offset
        """
    )

    with engine.connect() as conn:
        rows = conn.execute(sql, params).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int) -> dict[str, Any]:
    with engine.connect() as conn:
        row = (
            conn.execute(
                text(
                    """
                    SELECT *
                    FROM movies
                    WHERE movie_id = :mid
                    """
                ),
                {"mid": int(movie_id)},
            )
            .mappings()
            .fetchone()
        )
    if not row:
        raise HTTPException(status_code=404, detail="Movie not found")
    return dict(row)


@app.get("/genres")
def list_genres() -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT genre_id, genre_name FROM genres ORDER BY genre_name ASC")
        ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@app.get("/actors")
def list_actors(
    q: str | None = Query(default=None, description="Search by actor name"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    where = ""
    params: dict[str, Any] = {"limit": int(limit), "offset": int(offset)}
    if q and q.strip():
        where = "WHERE name LIKE :q"
        params["q"] = f"%{q.strip()}%"

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT actor_id, name, dob
                FROM actors
                {where}
                ORDER BY name ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
    return {"items": [dict(r) for r in rows], "limit": limit, "offset": offset}


@app.get("/movies/{movie_id}/genres")
def movie_genres(movie_id: int) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT g.genre_id, g.genre_name
                FROM movie_genres mg
                JOIN genres g ON g.genre_id = mg.genre_id
                WHERE mg.movie_id = :mid
                ORDER BY g.genre_name ASC
                """
            ),
            {"mid": int(movie_id)},
        ).mappings().all()
    return {"movie_id": int(movie_id), "items": [dict(r) for r in rows]}


@app.get("/movies/{movie_id}/actors")
def movie_actors(movie_id: int) -> dict[str, Any]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT a.actor_id, a.name, a.dob
                FROM movie_actors ma
                JOIN actors a ON a.actor_id = ma.actor_id
                WHERE ma.movie_id = :mid
                ORDER BY a.name ASC
                """
            ),
            {"mid": int(movie_id)},
        ).mappings().all()
    return {"movie_id": int(movie_id), "items": [dict(r) for r in rows]}

