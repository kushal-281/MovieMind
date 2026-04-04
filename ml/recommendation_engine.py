from ml.similarity_model import get_similar_movies
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("mysql+pymysql://root:Kushal%402004@localhost/moviemind")

def recommend(query):

    movies = get_similar_movies(query)
    result = []

    for movie in movies:

        movie_id = movie["movie_id"] if "movie_id" in movie else movie.get("movie_id")

        sql = f"""
        SELECT title, vote_average, poster_path
        FROM movies
        WHERE movie_id = {movie_id}
        """

        df = pd.read_sql(sql, engine)

        if not df.empty:
            row = df.iloc[0]

            result.append({
                "title": row["title"],
                "rating": row["vote_average"],
                "poster": row["poster_path"]
            })

    return result