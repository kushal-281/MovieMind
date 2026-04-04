import pandas as pd
from sqlalchemy import create_engine
import joblib

# -------- DB CONNECTION --------
engine = create_engine("mysql+pymysql://root:Kushal%402004@localhost/moviemind")

# -------- FETCH DATA --------
movies = pd.read_sql("SELECT movie_id, title, overview FROM movies", engine)
genres = pd.read_sql("SELECT * FROM genres", engine)
movie_genres = pd.read_sql("SELECT * FROM movie_genres", engine)

# -------- MERGE GENRES --------
df = movies.merge(movie_genres, on="movie_id")
df = df.merge(genres, on="genre_id")

# -------- GROUP GENRES --------
df = df.groupby("movie_id").agg({
    "title": "first",
    "overview": "first",
    "genre_name": lambda x: " ".join(x)
}).reset_index()

# -------- COMBINE FEATURES --------
df["tags"] = df["overview"].fillna('') + " " + df["genre_name"]

# -------- SAVE --------
joblib.dump(df, "../data/processed_data.pkl")

print("PKL file created successfully")