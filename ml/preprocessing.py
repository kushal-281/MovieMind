import pandas as pd
from config.database import engine

def load_data():
    movies = pd.read_sql("""
        SELECT movie_id, title, overview, vote_average, poster_path
        FROM movies
    """, engine)

    genres = pd.read_sql("""
        SELECT mg.movie_id, g.genre_name
        FROM movie_genres mg
        JOIN genres g ON mg.genre_id = g.genre_id
    """, engine)

    actors = pd.read_sql("""
        SELECT ma.movie_id, a.name
        FROM movie_actors ma
        JOIN actors a ON ma.actor_id = a.actor_id
    """, engine)

    return movies, genres, actors


def preprocess():
    movies, genres, actors = load_data()

    genres = genres.groupby("movie_id")["genre_name"].apply(lambda x: " ".join(x)).reset_index()
    actors = actors.groupby("movie_id")["name"].apply(lambda x: " ".join(x)).reset_index()

    df = movies.merge(genres, on="movie_id", how="left")
    df = df.merge(actors, on="movie_id", how="left")

    df["tags"] = (
        df["overview"].fillna('') + " " +
        df["genre_name"].fillna('') + " " +
        df["name"].fillna('')
    )

    return df