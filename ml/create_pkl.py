import pandas as pd
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import joblib

# -------- DB CONNECTION --------
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url:
    engine = create_engine(db_url)
else:
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    name = os.getenv("DB_NAME", "movieMind")
    engine = create_engine(
        URL.create(
            "mysql+pymysql",
            username=user,
            password=password,
            host=host,
            port=3306,
            database=name,
        )
    )

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